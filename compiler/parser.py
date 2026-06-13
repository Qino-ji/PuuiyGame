from compiler.lexer import Lexer, Token, LexerError
from compiler.ast_nodes import *


class ParseError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"Parse error at line {line}, col {col}: {msg}")
        self.line = line
        self.col = col


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token("EOF", "", 0, 0)

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, token_type):
        tok = self.peek()
        if tok.type != token_type:
            raise ParseError(
                f"Expected {token_type}, got {tok.type} ({tok.value!r})",
                tok.line, tok.col
            )
        return self.advance()

    def skip_newlines(self):
        while self.peek().type == "NEWLINE":
            self.advance()

    def at(self, token_type):
        return self.peek().type == token_type

    def at_any(self, *types):
        return self.peek().type in types

    def match(self, token_type):
        if self.peek().type == token_type:
            return self.advance()
        return None

    def parse(self):
        stmts = []
        self.skip_newlines()
        while not self.at("EOF"):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        return Program(stmts)

    def parse_statement(self):
        tok = self.peek()

        if tok.type in ("VAR", "LET"):
            return self.parse_var_decl()
        if tok.type in ("FN", "FUNC"):
            return self.parse_fn_decl()
        if tok.type == "IF":
            return self.parse_if()
        if tok.type == "WHILE":
            return self.parse_while()
        if tok.type == "FOR":
            return self.parse_for()
        if tok.type == "RETURN":
            return self.parse_return()
        if tok.type == "PASS":
            self.advance()
            return PassStmt()
        if tok.type == "BREAK":
            self.advance()
            return BreakStmt()
        if tok.type == "CONTINUE":
            self.advance()
            return ContinueStmt()
        if tok.type == "IMPORT":
            return self.parse_import()
        if tok.type == "CLASS":
            return self.parse_class()

        return self.parse_expr_or_assignment()

    def parse_var_decl(self):
        self.advance()
        name = self.expect("IDENT").value
        var_type = None
        if self.match("COLON"):
            var_type = self.expect("IDENT").value
        expr = None
        if self.match("ASSIGN"):
            expr = self.parse_expression()
        return VarDecl(name, var_type, expr)

    def parse_fn_decl(self):
        self.advance()
        name = self.expect("IDENT").value
        self.expect("LPAREN")
        params = []
        if not self.at("RPAREN"):
            params.append(self.parse_param())
            while self.match("COMMA"):
                params.append(self.parse_param())
        self.expect("RPAREN")
        return_type = None
        if self.match("ARROW"):
            return_type = self.expect("IDENT").value
        body = self.parse_block()
        return FnDecl(name, params, return_type, body)

    def parse_param(self):
        tok = self.peek()
        if tok.type == "SELF":
            self.advance()
            return Param("self", None)
        name = self.expect("IDENT").value
        param_type = None
        if self.match("COLON"):
            if self.at("IDENT"):
                param_type = self.advance().value
            elif self.at("SELF"):
                param_type = self.advance().value
        return Param(name, param_type)

    def parse_block(self):
        self.expect("COLON")
        self.skip_newlines()
        if not self.at("INDENT"):
            return []
        self.advance()
        stmts = []
        while not self.at_any("DEDENT", "EOF"):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        if self.at("DEDENT"):
            self.advance()
        return stmts

    def parse_if(self):
        self.expect("IF")
        cond = self.parse_expression()
        body = self.parse_block()
        elifs = []
        self.skip_newlines()
        while self.at("DEDENT"):
            self.advance()
            self.skip_newlines()
        while self.at("ELIF"):
            self.advance()
            econd = self.parse_expression()
            ebody = self.parse_block()
            elifs.append(ElifClause(econd, ebody))
            self.skip_newlines()
            while self.at("DEDENT"):
                self.advance()
                self.skip_newlines()
        else_body = None
        if self.at("ELSE"):
            self.advance()
            else_body = self.parse_block()
        return IfStmt(cond, body, elifs, else_body)

    def parse_while(self):
        self.expect("WHILE")
        cond = self.parse_expression()
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_for(self):
        self.expect("FOR")
        var_name = self.expect("IDENT").value
        self.expect("IN")
        iterable = self.parse_expression()
        body = self.parse_block()
        return ForStmt(var_name, iterable, body)

    def parse_return(self):
        self.expect("RETURN")
        expr = None
        if not self.at_any("NEWLINE", "EOF", "DEDENT"):
            expr = self.parse_expression()
        return ReturnStmt(expr)

    def parse_import(self):
        self.expect("IMPORT")
        path = self.expect("STRING").value
        return ImportStmt(path)

    def parse_class(self):
        self.expect("CLASS")
        name = self.expect("IDENT").value
        parent = None
        if self.match("LPAREN"):
            parent = self.parse_expression()
            self.expect("RPAREN")
        body = self.parse_block()
        methods = []
        for stmt in body:
            if isinstance(stmt, FnDecl):
                methods.append(stmt)
        return ClassDecl(name, parent, methods)

    def parse_expr_or_assignment(self):
        expr = self.parse_expression()

        if self.at("ASSIGN") and isinstance(expr, Identifier):
            self.advance()
            val = self.parse_expression()
            return Assignment(expr.name, val)

        if self.at("ASSIGN") and isinstance(expr, DotAccess):
            self.advance()
            val = self.parse_expression()
            return DotAssignment(expr.obj, expr.attr, val)

        if self.at("ASSIGN") and isinstance(expr, IndexAccess):
            self.advance()
            val = self.parse_expression()
            return IndexAssignment(expr.obj, expr.index, val)

        if self.at_any("PLUS_ASSIGN", "MINUS_ASSIGN", "STAR_ASSIGN", "SLASH_ASSIGN"):
            op_tok = self.advance()
            val = self.parse_expression()
            op_map = {
                "PLUS_ASSIGN": "+",
                "MINUS_ASSIGN": "-",
                "STAR_ASSIGN": "*",
                "SLASH_ASSIGN": "/"
            }
            bin_op = op_map[op_tok.type]
            if isinstance(expr, Identifier):
                return Assignment(
                    expr.name,
                    BinOp(bin_op, Identifier(expr.name), val)
                )

        return ExprStmt(expr)

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.at("OR"):
            self.advance()
            right = self.parse_and()
            left = BinOp("or", left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.at("AND"):
            self.advance()
            right = self.parse_not()
            left = BinOp("and", left, right)
        return left

    def parse_not(self):
        if self.at("NOT"):
            self.advance()
            operand = self.parse_not()
            return UnaryOp("not", operand)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()
        while self.at_any("EQ", "NEQ", "LT", "GT", "LTE", "GTE"):
            op = self.advance().value
            right = self.parse_additive()
            left = BinOp(op, left, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.at_any("PLUS", "MINUS"):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinOp(op, left, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.at_any("STAR", "SLASH", "PERCENT"):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self):
        if self.at("MINUS"):
            self.advance()
            operand = self.parse_unary()
            return UnaryOp("-", operand)
        if self.at("PLUS"):
            self.advance()
            return self.parse_unary()
        return self.parse_postfix()

    def parse_postfix(self):
        left = self.parse_primary()
        while True:
            if self.match("DOT"):
                attr_tok = self.peek()
                if attr_tok.type in ("IDENT", "NEW", "SELF"):
                    self.advance()
                else:
                    self.expect("IDENT")
                    attr_tok = self.tokens[self.pos - 1]
                attr = attr_tok.value
                if self.at("LPAREN"):
                    self.advance()
                    args = self.parse_args()
                    self.expect("RPAREN")
                    left = FuncCall(DotAccess(left, attr), args)
                else:
                    left = DotAccess(left, attr)
            elif self.match("LPAREN"):
                args = self.parse_args()
                self.expect("RPAREN")
                left = FuncCall(left, args)
            elif self.match("LBRACKET"):
                idx = self.parse_expression()
                self.expect("RBRACKET")
                left = IndexAccess(left, idx)
            else:
                break
        return left

    def parse_primary(self):
        tok = self.peek()

        if tok.type == "INT":
            self.advance()
            return NumberLiteral(tok.value)
        if tok.type == "FLOAT":
            self.advance()
            return NumberLiteral(tok.value)
        if tok.type == "STRING":
            self.advance()
            return StringLiteral(tok.value)
        if tok.type == "TRUE":
            self.advance()
            return BoolLiteral(True)
        if tok.type == "FALSE":
            self.advance()
            return BoolLiteral(False)
        if tok.type == "NULL":
            self.advance()
            return NoneLiteral()
        if tok.type in ("IDENT", "SELF"):
            self.advance()
            return Identifier(tok.value)
        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expression()
            self.expect("RPAREN")
            return expr
        if tok.type == "LBRACKET":
            return self.parse_array()
        if tok.type == "LBRACE":
            return self.parse_dict()

        raise ParseError(
            f"Unexpected token {tok.type} ({tok.value!r})",
            tok.line, tok.col
        )

    def parse_array(self):
        self.expect("LBRACKET")
        elems = []
        if not self.at("RBRACKET"):
            elems.append(self.parse_expression())
            while self.match("COMMA"):
                elems.append(self.parse_expression())
        self.expect("RBRACKET")
        return ArrayLiteral(elems)

    def parse_dict(self):
        self.expect("LBRACE")
        keys = []
        vals = []
        if not self.at("RBRACE"):
            if self.at("IDENT"):
                k = StringLiteral(self.advance().value)
            else:
                k = self.parse_expression()
            self.expect("COLON")
            v = self.parse_expression()
            keys.append(k)
            vals.append(v)
            while self.match("COMMA"):
                if self.at("IDENT"):
                    k = StringLiteral(self.advance().value)
                else:
                    k = self.parse_expression()
                self.expect("COLON")
                v = self.parse_expression()
                keys.append(k)
                vals.append(v)
        self.expect("RBRACE")
        return DictLiteral(keys, vals)

    def parse_args(self):
        args = []
        if not self.at("RPAREN"):
            args.append(self.parse_expression())
            while self.match("COMMA"):
                args.append(self.parse_expression())
        return args


def parse_source(source):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()