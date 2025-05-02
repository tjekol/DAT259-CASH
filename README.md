# CA$H

- [x] Lexer
- [x] Parser
- [x] Semantic analysis
- [x] Interpreter
- [x] Compiler

![illustration](./illustration.png)

### Lexer: How to check Tokens?

1. Set path and aliases
   ```
   export CLASSPATH=".:/usr/local/bin/antlr-4.13.2-complete.jar:$CLASSPATH"
   alias antlr='java -jar /usr/local/bin/antlr-4.13.2-complete.jar'
   alias antdbg='java org.antlr.v4.gui.TestRig'
   ```
2. Generate lexer and parser
   ```
   antlr CASHTokens.g4 -o gen
   ```
3. Compile lexer and scanner
   ```
   javac gen/*.java
   ```
4. Debug language

   ```
   antdbg <LanugageFile> tokens -tokens <testFile>
   ```

   - Example:
     ```
     antdbg CASHTokens tokens -tokens Example\ code/helloWorld.csh
     ```

### Interpreter: Generate visitor

```
antlr4 -Dlanguage=Python3 CASH.g4 -o interpreter/cash -visitor
```

Run interpreter

```
python3 interpreter/main.py
```

### Compiler: Compile a file

Install llvmlite

```
pip install llvmlite==0.44.0
```

#### Compile a file
Example for `helloWorld.cash`

```
antlr4 -Dlanguage=Python3 CASH.g4 -o compiler/cash -visitor
python3 compiler/compiler.py example_code/helloWorld.csh
```
