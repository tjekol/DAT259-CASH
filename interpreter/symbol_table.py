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
        self.types = {}

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
