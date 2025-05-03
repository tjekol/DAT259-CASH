from __future__ import annotations
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

    def __init__(self, next: SymbolTable | None = None):
        self.storage = {}
        self.tasks = {}
        self.types = {}
        self.next = next

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
    
    def is_defined(self, name: str):
        result = name in self.storage
        if not result and self.next is not None:
            return self.next.is_defined(name)
        return result

    def resister_var_name(self, name: str):
        self.types[name] = {"string", "integer", "float"}
