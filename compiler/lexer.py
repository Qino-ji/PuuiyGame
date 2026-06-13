import re


KEYWORDS = [
    "fn", "func", "var", "let", "if", "elif", "else",
    "while", "for", "in", "return", "pass", "break",
    "continue", "import", "from", "class", "extends",
    "new", "self", "true", "false", "null", "and", "or",
    "not", "signal", "emit"
]

TOKEN_TYPES = [
    ("NUMBER", r"\d+(\.\d+)?"),
    ("STRING_DQ", r'"[^"]*"'),
    ("STRING_SQ", r"'[^']*'"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("ARROW", r"->"),
    ("COLON", r":"),
    ("DOT", r"\."),
    ("COMMA", r","),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("EQ", r"=="),
    ("NEQ", r"!="),
    ("LTE", r"<="),
    ("GTE", r">="),
    ("LT", r"<"),
    ("GT", r">"),
    ("ASSIGN", r"="),
    ("PLUS_ASSIGN", r"\+="),
    ("MINUS_ASSIGN", r"-="),
    ("STAR_ASSIGN", r"\*="),
    ("SLASH_ASSIGN", r"/="),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("PERCENT", r"%"),
    ("SEMICOLON", r";"),
    ("DOUBLE_COLON", r"::"),
    ("ELLIPSIS", r"\.\.\."),
]

KEYWORD_SET = set(KEYWORDS)


class Token:
    def __init__(self, token_type, value, line, col):
        self.type = token_type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.col})"


class LexerError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"Lexer error at line {line}, col {col}: {msg}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source):
        self.source = source
        self.line = 1
        self.col = 1
        self.tokens = []
        self.indent_stack = [0]

        combined = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_TYPES)
        self.regex = re.compile(combined)

    def tokenize(self):
        lines = self.source.split("\n")
        for line_idx, line_text in enumerate(lines):
            if line_text.strip() == "" or line_text.lstrip().startswith("#"):
                continue

            indent = len(line_text) - len(line_text.lstrip())
            current_indent = self.indent_stack[-1]

            if indent > current_indent:
                self.indent_stack.append(indent)
                self.tokens.append(Token("INDENT", indent, line_idx + 1, 1))
            elif indent < current_indent:
                while self.indent_stack[-1] > indent:
                    self.indent_stack.pop()
                    self.tokens.append(Token("DEDENT", indent, line_idx + 1, 1))
                if self.indent_stack[-1] != indent:
                    raise LexerError(
                        f"Indentation does not match any outer level",
                        line_idx + 1, 1
                    )

            stripped = line_text.lstrip()
            pos = 0
            line_num = line_idx + 1

            for match in self.regex.finditer(stripped):
                kind = match.lastgroup
                value = match.group()
                col = match.start() + 1

                if kind == "NUMBER":
                    if "." in value:
                        self.tokens.append(Token("FLOAT", float(value), line_num, col))
                    else:
                        self.tokens.append(Token("INT", int(value), line_num, col))
                elif kind in ("STRING_DQ", "STRING_SQ"):
                    self.tokens.append(Token("STRING", value[1:-1], line_num, col))
                elif kind == "IDENT":
                    if value in KEYWORD_SET:
                        self.tokens.append(Token(value.upper(), value, line_num, col))
                    else:
                        self.tokens.append(Token("IDENT", value, line_num, col))
                else:
                    self.tokens.append(Token(kind, value, line_num, col))

            self.tokens.append(Token("NEWLINE", "\\n", line_num, len(line_text)))

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token("DEDENT", 0, len(lines), 1))

        self.tokens.append(Token("EOF", "", len(lines) + 1, 1))
        return self.tokens