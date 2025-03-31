import sys
from antlr4 import *
from cash.CASHParser import CASHParser
from cash.CASHLexer import CASHLexer
from cash.CASHVisitor import CASHVisitor


class SymbolTable:

    def __init__(self):
        self.storage = {}

    def add_var(self, name: str, value: float):
        self.storage[name] = value

    def get_var(self, name: str):
        if name not in self.storage:
            raise KeyError(f"Variable {name} not found!!")
        return self.storage[name]


class InterpreterVisitor(CASHVisitor): 
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table


    def visitPrint(self, ctx: CASHParser.PrintContext):
        empty_string = " "
        if ctx.STRING() is not None: 
            string_token = ctx.STRING()
            empty_string += str(string_token)[1:-1]
           
        if ctx.IDENTIFIER() is not None: 
            name = str(ctx.IDENTIFIER())
            var = self.symbol_table.get_var(name)
            empty_string += str(var)

        print(str(empty_string))


    def visitCost(self, ctx: CASHParser.CostContext):
        name = str(ctx.IDENTIFIER())
        value = self.visit(ctx.expression())
        self.symbol_table.add_var(name,value)



    def visitMult(self, ctx: CASHParser.MultContext):
        return self.visit(ctx.getChild(0)) * self.visit(ctx.getChild(2))
    
    def visitAdd(self, ctx: CASHParser.AddContext):
        return self.visit(ctx.getChild(0)) + self.visit(ctx.getChild(2))
    
    def visitDiv(self, ctx: CASHParser.DivContext):
        return self.visit(ctx.getChild(0)) / self.visit(ctx.getChild(2))
    
    def visitSub(self, ctx: CASHParser.SubContext):
        return self.visit(ctx.getChild(0)) - self.visit(ctx.getChild(2))
    
    def visitComparison(self, ctx: CASHParser.ComparisonContext):
        left = self.visit(ctx.getChild(0))
        right = self.visit(ctx.getChild(ctx.getChildCount()-1))

        if ctx.COMPARE_EQ() is not None:
            return left == right 
        elif ctx.COMPARE_LT() is not None: 
            return left < right 
        elif ctx.COMPARE_GT() is not None: 
            return left > right 
        
    def visitDiscount(self, ctx: CASHParser.DiscountContext):
        exp1 = self.visit(ctx.expression())
        name = str(ctx.IDENTIFIER())
        exp2 = self.symbol_table.get_var(name)
        exp2 = exp2 - (exp2 * (float(exp1) / 100))
        self.symbol_table.add_var(name, exp2)

    def visitNum(self, ctx: CASHParser.NumContext):
        return float(str(ctx.NUMBER()).replace(",", "."))
    
    def visitVar(self, ctx: CASHParser.VarContext):
        name = str(ctx.IDENTIFIER())
        var = self.symbol_table.get_var(name)
        return var
        
    



def main():

    input_stream = FileStream("./example_code/calc.csh", encoding="utf-8")
    lexer = CASHLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = CASHParser(token_stream)
    tree = parser.program()
    table = SymbolTable()
    visitor = InterpreterVisitor(table)
    visitor.visit(tree)
    # print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main()