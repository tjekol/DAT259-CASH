import sys
from antlr4 import *
from cash.CASHParser import CASHParser
from cash.CASHLexer import CASHLexer
from cash.CASHVisitor import CASHVisitor
from symbol_table import SymbolTable
from typing import Literal

CASH_TYP = Literal["string", "integer", "float", "boolean"]

class ExitCall(Exception):
    pass

class UndefinedVarRef(Exception):
    def __init__(self, name: str):
        self.name = name

class VarAlreadyDefined(Exception):
    def __init__(self, name: str):
        self.name = name

class UnsoundTypes(Exception):
    def __init__(self, name: str, expected: set[CASH_TYP], actual: set[CASH_TYP]):
        self.name = name
        self.expected = expected
        self.actual = actual

class TypeChecker(CASHVisitor): 
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.current_pushdown = set()

    def visitVar(self, ctx: CASHParser.VarContext):
        name = str(ctx.IDENTIFIER())
        result_types = self.current_pushdown.intersection(self.symbol_table.types[name])
        if len(result_types) == 0:
            raise UnsoundTypes(name, self.current_pushdown, self.symbol_table.types[name])
        else:
            self.symbol_table.types[name] = result_types
            return result_types
        
    def visitInt(self, ctx: CASHParser.IntContext):
        return {'integer'}
    
    def visitFloat(self, ctx: CASHParser.FloatContext):
        return {'float'}
    
    def visitNested(self, ctx: CASHParser.NestedContext):
        return self.visit(ctx.expression())
    
    def visitCost(self, ctx: CASHParser.CostContext):
        self.current_pushdown = {"integer", "float"}
        name = str(ctx.IDENTIFIER())
        admissable_types = self.visit(ctx.expression())
        self.symbol_table.types[name] = admissable_types

    def visitAdd(self, ctx: CASHParser.AddContext):
        self.current_pushdown = {"integer", "float"}
        lt = self.visit(ctx.getChild(0))
        rt = self.visit(ctx.getChild(2))
        if "float" in lt or "float" in rt:
            return {"float"}
        else:
            return {"integer"}
    
    def visitSub(self, ctx: CASHParser.SubContext):
        self.current_pushdown = {"integer", "float"}
        lt = self.visit(ctx.getChild(0))
        rt = self.visit(ctx.getChild(2))
        if "float" in lt or "float" in rt:
            return {"float"}
        else:
            return {"integer"}
    
    def visitMult(self, ctx: CASHParser.MultContext):
        self.current_pushdown = {"integer", "float"}
        lt = self.visit(ctx.getChild(0))
        rt = self.visit(ctx.getChild(2))
        if "float" in lt or "float" in rt:
            return {"float"}
        else:
            return {"integer"}

    def visitDiv(self, ctx: CASHParser.DivContext):
        self.current_pushdown = {"integer", "float"}
        lt = self.visit(ctx.getChild(0))
        rt = self.visit(ctx.getChild(2))
        if "float" in lt or "float" in rt:
            return {"float"}
        else:
            return {"integer"}

    def visitDiscount(self, ctx: CASHParser.DiscountContext):
        name = str(ctx.IDENTIFIER())
        self.current_pushdown = {"integer", "float"}
        discount_type = self.visit(ctx.expression())
        self.symbol_table.types[name] = {"float"} 
        # TODO discount always returns float
    
    def visitAsk(self, ctx: CASHParser.AskContext):
        name = str(ctx.IDENTIFIER())
        self.symbol_table.types[name] = {"float"}

    def visitCond_mod(self, ctx: CASHParser.Cond_modContext):
        for c, stmt in zip(ctx.comparison(), ctx.main_stmt()):
            self.visit(c)
            self.visit(stmt)
        self.visit(ctx.main_stmt(len(ctx.comparison())))

    def visitScan_mod(self, ctx: CASHParser.Scan_modContext):
        self.visit(ctx.comparison())
        for stmt in ctx.main_stmt():
            self.visit(stmt)

    def visitComparison(self, ctx: CASHParser.ComparisonContext):
        self.current_pushdown = {"integer", "float"}
        self.visit(ctx.getChild(0))
        self.visit(ctx.getChild(ctx.getChildCount() - 1))
        return {"boolean"}

    def summarize_types(self):
        for var_name in self.symbol_table.types.keys():
            types = self.symbol_table.types[var_name]
            if len(types) == 1:
                print(f"{var_name} is {types.__iter__().__next__()}")
            else:
                print(f"Error: {var_name} is unclear!")
def main():
    # input_stream = FileStream("./example_code/calc.csh", encoding="utf-8")
    # input_stream = FileStream("./example_code/ifThenElse.csh", encoding="utf-8")
    input_stream = FileStream("./example_code/int_float.csh", encoding="utf-8")
    # input_stream = FileStream("./example_code/while.csh", encoding="utf-8")

    lexer = CASHLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = CASHParser(token_stream)
    tree = parser.program()
    symbol_table = SymbolTable()

    # visitor = InterpreterVisitor(symbol_table)
    # visitor.visit(tree)

    type_check = TypeChecker(symbol_table)
    try:
        type_check.visit(tree)
        type_check.summarize_types()
    except UnsoundTypes as e:
        print(f"Error: {e.name} is of the wrong type! Exptected {e.expected} but was {e.actual}")
    except VarAlreadyDefined as e:
        print(f"Error: {e.name} already exists")
    except UndefinedVarRef as e:
        print(f"Error: {e.name} does not exist")

if __name__ == '__main__':
    main()