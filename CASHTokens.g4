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
NOT_KEYWORD : 'NOT';
AND_KEYWORD : 'AND';
OR_KEYWORD : 'OR';

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

SOP_CONCAT : '++';
SOP_SPLIT : '//';

COND_CONF : 'CONFIRM';
COND_CHECK : 'CHECK_AGAIN';
COND_FALLBACK : 'FALLBACK';

COMPARE_EQ : '=';
COMPARE_LT : '<';
COMPARE_LTE : '<=';
COMPARE_GT : '>';
COMPARE_GTE : '>=';

INT: '-'? DIGIT+;
FLOAT: '-'? DIGIT+ ',' DIGIT+;

COMMENT : 'NOTE' (~[\r\n])* DOLLAR NEWLINE -> skip;
NEWLINE : '\r'? '\n' [ \r\n\t]*;
WHITESPACE : [ \r\n\t]+ -> skip;

STRING : '"' (~["])* '"';

fragment CHAR : [a-zA-ZåæøÅÆØ];
fragment CHAR_PLUS : CHAR | '-' | INT;
fragment DIGIT : [0-9];
IDENTIFIER : CHAR CHAR_PLUS*;