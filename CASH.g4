grammar CASH;
import CASHTokens;

program : START_KEYWORD NEWLINE (main_stmt | cond_mod | scan_mod | task_mod)* END_KEYWORD NEWLINE?;

main_stmt : statement DOLLAR NEWLINE;

statement : COST_KEYWORD IDENTIFIER COMPARE_EQ expression # cost
        | PRINT_KEYWORD STRING (COMMA IDENTIFIER)? # print
        | DISCOUNT_KEYWORD OPEN_PAREN expression COMMA IDENTIFIER CLOSE_PAREN # discount
        | ASK_KEYWORD IDENTIFIER COMPARE_EQ STRING # ask
        | DO_TASK IDENTIFIER OPEN_PAREN expression CLOSE_PAREN # todo;


scan_mod : SCAN_KEYWORD OPEN_PAREN comparison CLOSE_PAREN COLON NEWLINE? main_stmt* DOLLAR NEWLINE?;

cond_mod : COND_CONF comparison COLON NEWLINE? main_stmt
           COND_CHECK comparison COLON NEWLINE? main_stmt
           COND_FALLBACK COLON NEWLINE? main_stmt;

task_mod : START_TASK IDENTIFIER OPEN_PAREN TASK_INPUT COLON IDENTIFIER CLOSE_PAREN COLON NEWLINE? (scan_mod |main_stmt )* END_TASK IDENTIFIER NEWLINE?;

expression : expression OP_MULT expression # mult 
    | expression OP_ADD expression # add 
    | expression OP_SUB expression # sub 
    | expression OP_DIV expression # div 
    | NUMBER # num
    | IDENTIFIER # var ;  


comparison : expression (COMPARE_EQ | COMPARE_LT | COMPARE_GT) expression ;
