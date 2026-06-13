class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VarDecl(ASTNode):
    def __init__(self, name, var_type, expr, is_const=False):
        self.name = name
        self.var_type = var_type
        self.expr = expr
        self.is_const = is_const

class FnDecl(ASTNode):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

class Param(ASTNode):
    def __init__(self, name, param_type=None):
        self.name = name
        self.param_type = param_type

class ReturnStmt(ASTNode):
    def __init__(self, expr=None):
        self.expr = expr

class IfStmt(ASTNode):
    def __init__(self, condition, body, elif_clauses=None, else_body=None):
        self.condition = condition
        self.body = body
        self.elif_clauses = elif_clauses or []
        self.else_body = else_body

class ElifClause(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForStmt(ASTNode):
    def __init__(self, var_name, iterable, body):
        self.var_name = var_name
        self.iterable = iterable
        self.body = body

class Assignment(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class DotAssignment(ASTNode):
    def __init__(self, obj, attr, expr):
        self.obj = obj
        self.attr = attr
        self.expr = expr

class IndexAssignment(ASTNode):
    def __init__(self, obj, index, expr):
        self.obj = obj
        self.index = index
        self.expr = expr

class BinOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class NumberLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class BoolLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class NoneLiteral(ASTNode):
    pass

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class FuncCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class DotAccess(ASTNode):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

class IndexAccess(ASTNode):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

class ArrayLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class DictLiteral(ASTNode):
    def __init__(self, keys, values):
        self.keys = keys
        self.values = values

class PassStmt(ASTNode):
    pass

class BreakStmt(ASTNode):
    pass

class ContinueStmt(ASTNode):
    pass

class ImportStmt(ASTNode):
    def __init__(self, path):
        self.path = path

class ExprStmt(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class ClassDecl(ASTNode):
    def __init__(self, name, parent, methods):
        self.name = name
        self.parent = parent
        self.methods = methods
