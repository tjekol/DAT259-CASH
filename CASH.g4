grammar CASH;
import CASHTokens;

program : START_KEYWORD NEWLINE (main_stmt | cond_mod | scan_mod | task_mod)* END_KEYWORD NEWLINE?;

main_stmt : statement DOLLAR NEWLINE;

statement : COST_KEYWORD expression COMPARE_EQ expression # cost
        | PRINT_KEYWORD STRING (COMMA expression)? # print
        | DISCOUNT_KEYWORD OPEN_PAREN expression COMMA expression CLOSE_PAREN # discount
        | ASK_KEYWORD expression COMPARE_EQ STRING # ask
        | DO_TASK IDENTIFIER OPEN_PAREN expression CLOSE_PAREN # todo;


scan_mod : SCAN_KEYWORD OPEN_PAREN comparison CLOSE_PAREN COLON NEWLINE? main_stmt*;

cond_mod : COND_CONF expression COMPARE_GT expression COLON NEWLINE? main_stmt
           COND_CHECK expression COMPARE_GT expression COLON NEWLINE? main_stmt
           COND_FALLBACK COLON NEWLINE? main_stmt;

task_mod : START_TASK IDENTIFIER OPEN_PAREN TASK_INPUT COLON IDENTIFIER CLOSE_PAREN COLON NEWLINE? (scan_mod |main_stmt )* END_TASK IDENTIFIER NEWLINE?;

expression : expression OP_MULT expression
    | expression OP_ADD expression
    | expression OP_SUB expression
    | expression OP_DIV expression
    | NUMBER
    | IDENTIFIER;

comparison : expression (COMPARE_EQ | COMPARE_LT | COMPARE_GT) expression;
