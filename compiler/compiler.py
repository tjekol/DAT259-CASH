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

# --- LLVM MODULE SETUP ---

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

# --- LLVM TYPE DEFINITIONS ---

BYTE_TYPE = ir.IntType(8)  # Represents a single byte (char)
DEFAULT_INT = ir.IntType(32)  # Used for integers and main() return type
PRINTF_TYPE = ir.FunctionType(DEFAULT_INT, (ir.PointerType(BYTE_TYPE),), var_arg=True)  # printf signature
MAIN_TYPE = ir.FunctionType(DEFAULT_INT, ())  # int main()

# --- CASH TO LLVM COMPILER VISITOR ---

class Compiler(CASHVisitor):
    """
    The main compiler class that walks the parse tree
    and generates LLVM IR for each supported CASH construct.
    """

    def __init__(self, source_file: Path):
        self.source_file = source_file
        self.module = init_module(source_file)
        self.uses_c_printf = None  # Lazy initialization of printf
        self.current_builder = None  # Will build IR in current basic block
        self.constant_counter = 0  # For generating unique global string names

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

        # Visit each top-level statement (e.g., RECEIPT "Hello")
        for child in ctx.children:
            self.visit(child)

        # Add return 0 to end main
        self.current_builder.ret(ir.Constant(DEFAULT_INT, 0))

    def visitPrint(self, ctx: CASHParser.PrintContext):
        """
        Emit IR to print a string using printf.
        Currently supports only string literals.
        """
        expr = ctx.expression()
        if expr and expr.str_lit() and expr.str_lit().STRING():
            string_node = expr.str_lit().STRING()
            value = str(string_node)[1:-1] + "\n\0"  # Strip quotes + add newline and null terminator
            value_bytes = value.encode()

            # Create a constant array for the string
            array_type = ir.ArrayType(BYTE_TYPE, len(value_bytes))
            const_val = ir.Constant(array_type, bytearray(value_bytes))

            # Declare it as a global constant
            var_name = self.next_constant()
            glob = ir.GlobalVariable(self.module, array_type, name=var_name)
            glob.global_constant = True
            glob.initializer = const_val

            # Convert array to pointer and call printf
            ptr = self.current_builder.bitcast(glob, ir.PointerType(BYTE_TYPE))
            self.current_builder.call(self.with_printf(), [ptr])

    def write_llvm_file(self):
        """
        Output the generated LLVM IR to a .ll file for inspection or compilation.
        """
        filename = (str(self.source_file).split('/')[1]).split(".")[0]
        source_file = "compiler/" + filename + '.ll'
        with open(source_file, "w") as out:
            out.write(str(self.module))

    def call_llvm_compile(self):
        """
        Use clang to compile the .ll file into a native executable.
        """
        filename = (str(self.source_file).split('/')[1]).split(".")[0]
        source_file = "compiler/" + filename + '.ll'
        subprocess.run(['clang', source_file, '-w', '-o', source_file.split(".")[0]])

    def print_llvm(self):
        """
        Return the LLVM IR as a string (for debugging).
        """
        return str(self.module)

# --- MAIN ENTRY POINT ---

def main():
    """
    The main driver: parses the source file, runs the compiler,
    writes the IR, compiles it, and runs the resulting program.
    """
    if len(sys.argv) >= 2:
        fname = sys.argv[1]
        fpath = Path(fname)

        # --- Parse the CASH source using ANTLR ---
        input_stream = FileStream(fname, encoding="utf-8")
        lexer = CASHLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = CASHParser(token_stream)
        tree = parser.program()
        print(tree.toStringTree(recog=parser))


        # --- Compile the parse tree to LLVM ---
        compiler = Compiler(fpath)
        compiler.visit(tree)

        # --- Optionally print LLVM IR for debugging ---
        if "--debug" in sys.argv:
            print(compiler.print_llvm())

        # --- Compile and run ---
        compiler.write_llvm_file()
        compiler.call_llvm_compile()
        fpath = (str(fpath).split("/")[1]).split(".")[0]
        subprocess.run(f"./compiler/{fpath}")
    else:
        print("Usage: python compiler/compiler.py path/to/file.cash")

if __name__ == "__main__":
    main()
