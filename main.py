import sys
from antlr4 import *
from cash.CASHParser import CASHParser
from cash.CASHLexer import CASHLexer
from cash.CASHVisitor import CASHVisitor


class Task: 
    def __init__(self, name: str, param_names: list, body):
        self.name = name
        self.param_names = param_names
        self.body = body

    def execute(self, visitor: 'InterpreterVisitor', param_values): 

    
        for name, value in zip(self.param_names, param_values):
            visitor.symbol_table.add_var(name, value)

        for stmt in self.body:
            visitor.visit(stmt)


class SymbolTable:

    def __init__(self):
        self.storage = {}
        self.tasks = {}

    def add_var(self, name: str, value: float):
        self.storage[name] = value

    def get_var(self, name: str):
        if name not in self.storage:
            raise KeyError(f"Variable {name} not found!!")
        return self.storage[name]
    

    def add_task(self, task: Task):
        self.tasks[task.name] = task 

    def get_task(self, name: str): 
        return self.tasks[name]

class InterpreterVisitor(CASHVisitor): 
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def visitPrint(self, ctx: CASHParser.PrintContext):
        empty_string = ""
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
        elif ctx.COMPARE_LTE() is not None:
            return left <= right 
        elif ctx.COMPARE_GT() is not None: 
            return left > right
        elif ctx.COMPARE_GTE() is not None:
            return left >= right

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
    
    def visitAsk(self, ctx: CASHParser.AskContext):
        prompt = str(ctx.STRING())[1:-1]
        value = float(input(f"{prompt}: "))
        name = str(ctx.IDENTIFIER()) 
        self.symbol_table.add_var(name, value)

    def visitCond_mod(self, ctx: CASHParser.Cond_modContext):
        for c, stmt in zip(ctx.comparison(), ctx.main_stmt()):
            if self.visit(c):
                self.visit(stmt)
                return
        self.visit(ctx.main_stmt(len(ctx.comparison())))

    def visitScan_mod(self, ctx: CASHParser.Scan_modContext):
        isSatisfied = self.visit(ctx.comparison())
        while isSatisfied:
            for stmt in ctx.main_stmt():
                self.visit(stmt)

            isSatisfied = self.visit(ctx.comparison())

    def visitTask_mod(self, ctx: CASHParser.Task_modContext):
        name = str(ctx.IDENTIFIER(0))
        params = self.visit(ctx.param_list())
        task_body = list(ctx.task_body().getChildren())
        task = Task(name, params, task_body)
        self.symbol_table.add_task(task)

    def visitTodo(self, ctx: CASHParser.TodoContext):
        name = str(ctx.IDENTIFIER())
        
        if ctx.actual_param_list():
            params = self.visit(ctx.actual_param_list())
        else:
            params = []

        task = self.symbol_table.get_task(name)

        task.execute(self, params)

    def visitParam_list(self, ctx: CASHParser.Param_listContext):
        index = 0
        curr = ctx.IDENTIFIER(index)
        result = []
        while curr is not None: 
            result.append(str(curr))
            index += 1
            curr = ctx.IDENTIFIER(index)
        return result
    
    def visitActual_param_list(self, ctx: CASHParser.Actual_param_listContext):
        return [self.visit(expr) for expr in ctx.expression()]

def main():
    input_stream = FileStream("./example_code/ifThenElse.csh", encoding="utf-8")
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