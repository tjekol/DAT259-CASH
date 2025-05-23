grammar CASH;
import CASHTokens;

program : START_KEYWORD NEWLINE (main_stmt | cond_mod | scan_mod | task_mod)* END_KEYWORD NEWLINE?;

main_stmt : statement DOLLAR NEWLINE;

statement : COST_KEYWORD IDENTIFIER COMPARE_EQ expression # cost
        | PRINT_KEYWORD (expression | STRING (COMMA expression)?) # print
        | DISCOUNT_KEYWORD OPEN_PAREN expression COMMA IDENTIFIER CLOSE_PAREN # discount
        | ASK_KEYWORD IDENTIFIER COMPARE_EQ STRING # ask
        | DO_TASK IDENTIFIER OPEN_PAREN actual_param_list CLOSE_PAREN # todo;

scan_mod : SCAN_KEYWORD OPEN_PAREN bool_expr CLOSE_PAREN COLON NEWLINE? main_stmt* DOLLAR NEWLINE?;

cond_mod : COND_CONF bool_expr COLON NEWLINE? main_stmt
        (COND_CHECK bool_expr COLON NEWLINE? main_stmt)*
        (COND_FALLBACK COLON NEWLINE? main_stmt)?;

task_mod : START_TASK IDENTIFIER OPEN_PAREN TASK_INPUT COLON param_list CLOSE_PAREN COLON NEWLINE? task_body END_TASK IDENTIFIER NEWLINE?;

task_body : (scan_mod | main_stmt | cond_mod)+;

actual_param_list : IDENTIFIER COLON expression (COMMA IDENTIFIER COLON expression)*;
param_list : IDENTIFIER (COMMA IDENTIFIER)*;

expression : OPEN_PAREN expression CLOSE_PAREN # nested
        | expression OP_MULT expression # mult
        | expression OP_ADD expression # add
        | expression OP_SUB expression # sub 
        | expression OP_DIV expression # div
        | expression SOP_CONCAT expression # concat
        | expression SOP_SPLIT expression # split
        | str_lit # strlit
        | FLOAT # float
        | INT # int
        | IDENTIFIER # var ;  

bool_expr : OPEN_PAREN bool_expr CLOSE_PAREN # nested_bool
        | NOT_KEYWORD bool_expr # not
        | bool_expr AND_KEYWORD bool_expr # and
        | bool_expr OR_KEYWORD bool_expr # or
        | comparison # comp ;

comparison : expression (COMPARE_EQ | COMPARE_LT | COMPARE_GT | COMPARE_GTE | COMPARE_LTE) expression;

str_lit : STRING;
