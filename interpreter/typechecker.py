import sys
from antlr4 import *
from cash.CASHParser import CASHParser
from cash.CASHLexer import CASHLexer
from cash.CASHVisitor import CASHVisitor
from symbol_table import SymbolTable
from typing import Literal

CASH_TYP = Literal["string", "integer", "float"]

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

    def summarize_types(self):
        for var_name in self.symbol_table.types.keys():
            types = self.symbol_table.types[var_name]
            if len(types) == 1:
                print(f"{var_name} er {types.__iter__().__next__()}")
            else:
                print(f"Feil: {var_name} er uklart!")
def main():
    input_stream = FileStream("./example_code/helloWorld.csh", encoding="utf-8")

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
        print(f"FEIL! Stedfortreter {e.name} har feil type! Det forventes å være {e.expected} mend den er {e.actual}")
    except VarAlreadyDefined as e:
        print(f"FEIL! Stedfortreter {e.name} finnast alt!")
    except UndefinedVarRef as e:
        print(f"FEIL! Stedfortreter {e.name} finnast ikkje")

if __name__ == '__main__':
    main()