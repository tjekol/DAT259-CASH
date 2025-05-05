import os
import subprocess
import sys
from pathlib import Path

import llvmlite.ir as ir
import llvmlite.binding as llvm

from antlr4 import *
from cash.CASHParser import CASHParser
from cash.CASHLexer import CASHLexer
from cash.CASHVisitor import CASHVisitor

def init_module(source_file: Path):
    """
    Initialize an LLVM module for the given source file.
    This sets up the target and data layout so LLVM knows how to emit code for the host system.
    """
    llvm.initialize()
    llvm.initialize_native_target()
    module = ir.Module(name=source_file.name)

    target = llvm.Target.from_default_triple()
    machine = target.create_target_machine()

    module.triple = machine.triple
    module.data_layout = str(machine.target_data)
    return module

BYTE_TYPE = ir.IntType(8) 
DEFAULT_INT = ir.IntType(32)  
FLOAT_TYPE = ir.FloatType()
PRINTF_TYPE = ir.FunctionType(DEFAULT_INT, (ir.PointerType(BYTE_TYPE),), var_arg=True) 
MAIN_TYPE = ir.FunctionType(DEFAULT_INT, ()) 


class Compiler(CASHVisitor):
    """
    The main compiler class that walks the parse tree
    and generates LLVM IR for each supported CASH construct.
    """

    def __init__(self, source_file: Path):
        self.source_file = source_file
        self.module = init_module(source_file)
        self.uses_c_printf = None  
        self.current_builder = None 
        self.constant_counter = 0 
        self.variables = {}  
        self.string_vars = {}

    def next_constant(self, prefix: str = "str"):
        """
        Generate a unique name for a new global string constant.
        This ensures no naming collisions between multiple string literals.
        """
        self.constant_counter += 1
        return f"{prefix}{self.constant_counter}"

    def with_printf(self):
        """
        Declare or return the printf function.
        Needed to call printf from generated LLVM IR.
        """
        if not self.uses_c_printf:
            func = ir.Function(self.module, PRINTF_TYPE, name="printf")
            self.uses_c_printf = func
        return self.uses_c_printf

    def visitProgram(self, ctx: CASHParser.ProgramContext):
        """
        Generate the LLVM IR for the main function.
        CASH starts execution here. Each statement is visited in order.
        """
        mainf = ir.Function(self.module, MAIN_TYPE, name="main")
        main_block = mainf.append_basic_block("entry")
        self.current_builder = ir.IRBuilder(main_block)
        
        for child in ctx.children:
            if hasattr(child, 'children'):
                for stmt in child.children:
                    self.visit(stmt)
            else:
                self.visit(child)

        self.current_builder.ret(ir.Constant(DEFAULT_INT, 0))

    def visitCost(self, ctx: CASHParser.CostContext):
        var_name = ctx.IDENTIFIER().getText()
        expr = ctx.expression()
        value = self.visit(expr)
        
        if isinstance(value, tuple):
            self.string_vars[var_name] = value
        else:  
            self.variables[var_name] = value

    def visitPrint(self, ctx: CASHParser.PrintContext):
        # case 1: String only 
        if ctx.STRING() and not ctx.expression():
            string_node = ctx.STRING()
            value = string_node.getText()[1:-1] + "\n\0"
            value_bytes = value.encode()

            array_type = ir.ArrayType(BYTE_TYPE, len(value_bytes))
            const_val = ir.Constant(array_type, bytearray(value_bytes))

            var_name = self.next_constant()
            glob = ir.GlobalVariable(self.module, array_type, name=var_name)
            glob.global_constant = True
            glob.initializer = const_val

            ptr = self.current_builder.bitcast(glob, ir.PointerType(BYTE_TYPE))
            self.current_builder.call(self.with_printf(), [ptr])
        
        # case 2: String and variable
        elif ctx.STRING() and ctx.expression():
            format_str = ctx.STRING().getText()[1:-1] + "%d\n\0"
            format_bytes = format_str.encode()
            
            array_type = ir.ArrayType(BYTE_TYPE, len(format_bytes))
            const_val = ir.Constant(array_type, bytearray(format_bytes))
            
            var_name = self.next_constant()
            glob = ir.GlobalVariable(self.module, array_type, name=var_name)
            glob.global_constant = True
            glob.initializer = const_val
            
            ptr = self.current_builder.bitcast(glob, ir.PointerType(BYTE_TYPE))
            var_value = self.visit(ctx.expression())
            self.current_builder.call(self.with_printf(), [ptr, var_value])
        
        # case 3: Variable only 
        elif ctx.expression():
            format_str = "%d\n\0"
            format_bytes = format_str.encode()
            
            array_type = ir.ArrayType(BYTE_TYPE, len(format_bytes))
            const_val = ir.Constant(array_type, bytearray(format_bytes))
            
            var_name = self.next_constant()
            glob = ir.GlobalVariable(self.module, array_type, name=var_name)
            glob.global_constant = True
            glob.initializer = const_val
            
            ptr = self.current_builder.bitcast(glob, ir.PointerType(BYTE_TYPE))
            var_value = self.visit(ctx.expression())
            self.current_builder.call(self.with_printf(), [ptr, var_value])


    def visitDiscount(self, ctx: CASHParser.DiscountContext):
        percentage = self.visit(ctx.expression()) 
        var_name = ctx.IDENTIFIER().getText()
        
        if var_name in self.variables:
            value = self.variables[var_name]
            hundred = ir.Constant(DEFAULT_INT, 100)
            
            # Calculate (100 - percentage)
            diff = self.current_builder.sub(hundred, percentage)
            # Multiply by value
            product = self.current_builder.mul(value, diff)
            # Divide by 100
            discounted = self.current_builder.sdiv(product, hundred)
            
            self.variables[var_name] = discounted

    def visitNested(self, ctx: CASHParser.NestedContext):
        return self.visit(ctx.expression())

    def visitMult(self, ctx: CASHParser.MultContext):
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return self.current_builder.mul(left, right)

    def visitAdd(self, ctx: CASHParser.AddContext):
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return self.current_builder.add(left, right)

    def visitSub(self, ctx: CASHParser.SubContext):
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return self.current_builder.sub(left, right)

    def visitDiv(self, ctx: CASHParser.DivContext):
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return self.current_builder.sdiv(left, right)

    def visitStrlit(self, ctx: CASHParser.StrlitContext):
        if ctx.STRING():
            value = ctx.STRING().getText()[1:-1] + "\0"
            value_bytes = value.encode()

            array_type = ir.ArrayType(BYTE_TYPE, len(value_bytes))
            const_val = ir.Constant(array_type, bytearray(value_bytes))

            var_name = self.next_constant()
            glob = ir.GlobalVariable(self.module, array_type, name=var_name)
            glob.global_constant = True
            glob.initializer = const_val

            ptr = self.current_builder.bitcast(glob, ir.PointerType(BYTE_TYPE))
            return (value, ptr)
        return ("", None)

    def visitFloat(self, ctx: CASHParser.FloatContext):
        # Convert comma to decimal point for float parsing
        float_str = ctx.FLOAT().getText().replace(',', '.')
        return ir.Constant(FLOAT_TYPE, float(float_str))

    def visitInt(self, ctx: CASHParser.IntContext):
        return ir.Constant(DEFAULT_INT, int(ctx.INT().getText()))

    def visitVar(self, ctx: CASHParser.VarContext):
        var_name = ctx.IDENTIFIER().getText()
        if var_name in self.variables:
            return self.variables[var_name]
        elif var_name in self.string_vars:
            return self.string_vars[var_name]
        return ir.Constant(DEFAULT_INT, 0)

    def write_llvm_file(self):
        """
        Output the generated LLVM IR to a .ll file for inspection or compilation.
        """
        filename = self.source_file.stem
        source_file = "compiler/" + filename + '.ll'
        with open(source_file, "w") as out:
            out.write(str(self.module))

    def call_llvm_compile(self):
        """
        Use clang to compile the .ll file into a native executable.
        """
        filename = self.source_file.stem
        source_file = "compiler/" + filename + '.ll'
        subprocess.run(['clang', source_file, '-w', '-o', source_file.split(".")[0]])

    def print_llvm(self):
        """
        Return the LLVM IR as a string.
        """
        return str(self.module)


def main():
    """
    The main driver: parses the source file, runs the compiler,
    writes the IR, compiles it, and runs the resulting program.
    """
    if len(sys.argv) >= 2:
        fname = sys.argv[1]
        fpath = Path(fname)

        # parse the CASH source using ANTLR 
        input_stream = FileStream(fname, encoding="utf-8")
        lexer = CASHLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = CASHParser(token_stream)
        tree = parser.program()
        print(tree.toStringTree(recog=parser))

        # compile the parse tree to LLVM 
        compiler = Compiler(fpath)
        compiler.visit(tree)

        # optionally print LLVM IR for debugging 
        if "--debug" in sys.argv:
            print(compiler.print_llvm())

        # compile and run
        compiler.write_llvm_file()
        compiler.call_llvm_compile()
        subprocess.run(f"./compiler/{fpath.stem}")
    else:
        print("Usage: python compiler.py path/to/file.csh [--debug]")

if __name__ == "__main__":
    main()