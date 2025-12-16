# Grammar & Design Notes

## Tokens
- **Keywords**: `start, end, int, float, if, else, while, print`
- **Delimiters**: `; , ( ) { }`
- **Operators**: `+ - * / == != < <= > >= = !`
- **Identifiers**: `[A-Za-z_][A-Za-z_0-9]*`
- **Numbers**: integers (`42`) and floats (`3.14`, `0.5`, `10.` `.` is not allowed alone)

## Grammar (EBNF-ish)

```
Program  := "start" StmtList "end"
StmtList := { Stmt }
Stmt     := VarDecl ';' | Assign ';' | Print ';' | IfStmt | WhileStmt | Block
VarDecl  := Type IDENT ( '=' Expr )?
Type     := "int" | "float"
Assign   := IDENT '=' Expr
Print    := 'print' '(' Expr ')'
IfStmt   := 'if' '(' Expr ')' Stmt [ 'else' Stmt ]
While    := 'while' '(' Expr ')' Stmt
Block    := '{' StmtList '}'
Expr     := Equality
Equality := Comparison ( ('==' | '!=') Comparison )*
Comparison := Term ( ('<' | '<=' | '>' | '>=') Term )*
Term     := Factor ( ('+' | '-') Factor )*
Factor   := Unary  ( ('*' | '/') Unary )*
Unary    := ('+'|'-'|'!') Unary | Primary
Primary  := NUMBER | IDENT | '(' Expr ')'
```

## Semantic Rules
- Variables must be declared before use.
- Re-declaration in the same scope is an error.
- Nested scopes via `{ ... }` blocks.
- Arithmetic type promotion: if any operand is float → result is float.
- Assignment type compatibility: int ← int; float ← (int|float) (int promoted).

## Intermediate Representation
Three-address code (TAC) format used:
- Expressions produce temporaries `t1, t2, ...`
- Statements produce labels and `goto` as needed for control flow.
- Print is lowered to `print v`

Example:
```
t1 = a + i
a = t1
if a > 6 goto L1
t2 = a + b
print t2
goto L2
L1:
print a
L2:
...
```

## Error Handling
- Lexer: reports invalid character sequences with position.
- Parser: reports unexpected tokens and what was expected.
- Semantic: reports use-before-declare, duplicate symbol, and type mismatch.
