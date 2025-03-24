lexer grammar CASHTokens;

START_KEYWORD : 'HELLO.';
END_KEYWORD : 'BYE.';

PERIOD : '.';
DOLLAR : '$';
COMMA : ',';
COLON : ':';

COST_KEYWORD : 'COST';
PRINT_KEYWORD : 'RECEIPT';
DISCOUNT_KEYWORD : 'DISCOUNT';
ASK_KEYWORD : 'ASK';
SCAN_KEYWORD : 'SCAN';

START_TASK : 'START TASK';
END_TASK : 'END';
DO_TASK : 'TODO';
TASK_INPUT : 'IN';

OPEN_PAREN : '(';
CLOSE_PAREN : ')';

OP_MULT : '*';
OP_ADD : '+';
OP_SUB : '-';
OP_DIV : '/';

COND_CONF : 'CONFIRM';
COND_CHECK : 'CHECK_AGAIN';
COND_FALLBACK : 'FALLBACK';

COMPARE_EQ : '=';
COMPARE_LT : '<';
COMPARE_GT : '>';



NUMBER: '-'? DIGIT+ (',' DIGIT+)?;
COMMENT : 'NOTE' (~[\r])* DOLLAR NEWLINE -> skip;
NEWLINE : '\r'? '\n' [ \r\n\t]*;
WHITESPACE : [ \r\n\t]+ -> skip;

STRING : '"' (~["])* '"';

fragment CHAR : [a-zA-ZåæøÅÆØ];
fragment CHAR_PLUS : CHAR | '-' | NUMBER;
fragment DIGIT : [0-9];
IDENTIFIER : CHAR CHAR_PLUS*;