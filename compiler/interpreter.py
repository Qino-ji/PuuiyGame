from compiler.ast_nodes import *
from compiler.builtins import (
    BuiltinFunction, FunctionDef, PuiClassDef, PuiClassInstance,
    ReturnSignal, BreakSignal, ContinueSignal, to_string,
    get_default_builtins
)


class BreakOut(Exception):
    pass


class ContinueOut(Exception):
    pass


class ReturnOut(Exception):
    def __init__(self, value):
        self.value = value


class InterpreterError(Exception):
    def __init__(self, msg, line=0, col=0):
        self.msg = msg
        self.line = line
        self.col = col
        if line:
            super().__init__(f"Runtime error at line {line}, col {col}: {msg}")
        else:
            super().__init__(f"Runtime error: {msg}")


class Env:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise InterpreterError(f"Undefined variable '{name}'")

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            try:
                self.parent.get(name)
                self.parent.set(name, value)
                return
            except InterpreterError:
                pass
        self.vars[name] = value

    def define(self, name, value):
        self.vars[name] = value

    def has(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


class Interpreter:
    def __init__(self):
        self.global_env = Env()
        self.builtins = get_default_builtins()
        for k, v in self.builtins.items():
            self.global_env.define(k, v)
        self._imported = {}
        self._classes = {}
        self._current_class = None

    def run(self, program):
        self.exec_block(program.statements, self.global_env)

    def exec_block(self, stmts, env):
        for stmt in stmts:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, node, env):
        if isinstance(node, VarDecl):
            self.exec_var_decl(node, env)
        elif isinstance(node, FnDecl):
            self.exec_fn_decl(node, env)
        elif isinstance(node, IfStmt):
            self.exec_if(node, env)
        elif isinstance(node, WhileStmt):
            self.exec_while(node, env)
        elif isinstance(node, ForStmt):
            self.exec_for(node, env)
        elif isinstance(node, ReturnStmt):
            val = None
            if node.expr:
                val = self.eval_expr(node.expr, env)
            raise ReturnOut(val)
        elif isinstance(node, Assignment):
            val = self.eval_expr(node.expr, env)
            env.set(node.name, val)
        elif isinstance(node, DotAssignment):
            obj = self.eval_expr(node.obj, env)
            val = self.eval_expr(node.expr, env)
            if isinstance(obj, PuiClassInstance):
                obj.set(node.attr, val)
            elif isinstance(obj, dict):
                obj[node.attr] = val
        elif isinstance(node, IndexAssignment):
            obj = self.eval_expr(node.obj, env)
            idx = self.eval_expr(node.index, env)
            val = self.eval_expr(node.expr, env)
            obj[int(idx)] = val
        elif isinstance(node, ExprStmt):
            self.eval_expr(node.expr, env)
        elif isinstance(node, PassStmt):
            pass
        elif isinstance(node, BreakStmt):
            raise BreakOut()
        elif isinstance(node, ContinueStmt):
            raise ContinueOut()
        elif isinstance(node, ImportStmt):
            self.exec_import(node, env)
        elif isinstance(node, ClassDecl):
            self.exec_class_decl(node, env)
        else:
            raise InterpreterError(f"Unknown statement type: {type(node).__name__}")

    def exec_var_decl(self, node, env):
        val = None
        if node.expr:
            val = self.eval_expr(node.expr, env)
        env.define(node.name, val)

    def exec_fn_decl(self, node, env):
        fn = FunctionDef(node.name, node.params, node.body, env)
        env.define(node.name, fn)

    def exec_if(self, node, env):
        cond = self.eval_expr(node.condition, env)
        if is_truthy(cond):
            self.exec_block(node.body, env)
            return
        for elifc in node.elif_clauses:
            cond = self.eval_expr(elifc.condition, env)
            if is_truthy(cond):
                self.exec_block(elifc.body, env)
                return
        if node.else_body:
            self.exec_block(node.else_body, env)

    def exec_while(self, node, env):
        while True:
            cond = self.eval_expr(node.condition, env)
            if not is_truthy(cond):
                break
            try:
                self.exec_block(node.body, env)
            except BreakOut:
                break
            except ContinueOut:
                continue

    def exec_for(self, node, env):
        iterable = self.eval_expr(node.iterable, env)
        if isinstance(iterable, list):
            for item in iterable:
                child_env = Env(env)
                child_env.define(node.var_name, item)
                try:
                    self.exec_block(node.body, child_env)
                except BreakOut:
                    break
                except ContinueOut:
                    continue
        elif isinstance(iterable, dict):
            for key in iterable:
                child_env = Env(env)
                child_env.define(node.var_name, key)
                try:
                    self.exec_block(node.body, child_env)
                except BreakOut:
                    break
                except ContinueOut:
                    continue
        else:
            raise InterpreterError(f"'{type(iterable).__name__}' is not iterable")

    def exec_class_decl(self, node, env):
        parent = None
        if node.parent:
            parent = self.eval_expr(node.parent, env)
        methods = {}
        init_method = None
        for method in node.methods:
            fn = FunctionDef(method.name, method.params, method.body, env)
            methods[method.name] = fn
            if method.name == "init":
                init_method = fn
        cls = PuiClassDef(node.name, parent, methods, init_method)
        self._classes[node.name] = cls
        env.define(node.name, cls)

    def exec_import(self, node, env):
        import os
        path = node.path
        if path in self._imported:
            for k, v in self._imported[path].items():
                env.define(k, v)
            return
        if not os.path.exists(path):
            raise InterpreterError(f"Import file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        from compiler.parser import parse_source
        tree = parse_source(source)
        mod_env = Env(self.global_env)
        self.exec_block(tree.statements, mod_env)

        self._imported[path] = {}
        for k, v in mod_env.vars.items():
            env.define(k, v)
            self._imported[path][k] = v

    def eval_expr(self, node, env):
        if isinstance(node, NumberLiteral):
            return node.value
        if isinstance(node, StringLiteral):
            return node.value
        if isinstance(node, BoolLiteral):
            return node.value
        if isinstance(node, NoneLiteral):
            return None
        if isinstance(node, Identifier):
            return env.get(node.name)
        if isinstance(node, BinOp):
            return self.eval_binop(node, env)
        if isinstance(node, UnaryOp):
            return self.eval_unaryop(node, env)
        if isinstance(node, FuncCall):
            return self.eval_func_call(node, env)
        if isinstance(node, DotAccess):
            return self.eval_dot_access(node, env)
        if isinstance(node, IndexAccess):
            return self.eval_index_access(node, env)
        if isinstance(node, ArrayLiteral):
            return [self.eval_expr(e, env) for e in node.elements]
        if isinstance(node, DictLiteral):
            d = {}
            for k, v in zip(node.keys, node.values):
                key = self.eval_expr(k, env)
                val = self.eval_expr(v, env)
                d[key] = val
            return d
        raise InterpreterError(f"Unknown expression: {type(node).__name__}")

    def eval_binop(self, node, env):
        if node.op == "and":
            left = self.eval_expr(node.left, env)
            if not is_truthy(left):
                return left
            return self.eval_expr(node.right, env)
        if node.op == "or":
            left = self.eval_expr(node.left, env)
            if is_truthy(left):
                return left
            return self.eval_expr(node.right, env)

        left = self.eval_expr(node.left, env)
        right = self.eval_expr(node.right, env)

        if node.op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return to_string(left) + to_string(right)
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            if isinstance(left, list):
                return left * int(right)
            return left * right
        if node.op == "/":
            return float(left) / float(right) if right != 0 else 0
        if node.op == "%":
            return float(left) % float(right) if right != 0 else 0
        if node.op == "==":
            return left == right
        if node.op == "!=":
            return left != right
        if node.op == "<":
            return left < right
        if node.op == ">":
            return left > right
        if node.op == "<=":
            return left <= right
        if node.op == ">=":
            return left >= right

        raise InterpreterError(f"Unknown operator: {node.op}")

    def eval_unaryop(self, node, env):
        val = self.eval_expr(node.operand, env)
        if node.op == "-":
            return -val
        if node.op == "not":
            return not is_truthy(val)
        raise InterpreterError(f"Unknown unary operator: {node.op}")

    def eval_func_call(self, node, env):
        fn_name = node.name
        args = [self.eval_expr(a, env) for a in node.args]

        if isinstance(fn_name, DotAccess):
            obj = self.eval_expr(fn_name.obj, env)
            method_name = fn_name.attr
            if isinstance(obj, PuiClassDef):
                if method_name == "new":
                    return self.call_class(obj, args)
                if method_name in obj.methods:
                    return self.call_function(obj.methods[method_name], args)
                raise InterpreterError(f"'{obj.name}' has no method '{method_name}'")
            if isinstance(obj, PuiClassInstance):
                method = obj.get(method_name)
                if method:
                    return self.call_function(method, args, obj)
                raise InterpreterError(f"'{obj.class_name}' has no method '{method_name}'")
            if isinstance(obj, dict):
                if method_name == "has":
                    return method_name in obj or args[0] in obj
                return obj.get(method_name)
            if isinstance(obj, list):
                return self._call_array_method(obj, method_name, args)
            if isinstance(obj, str):
                return self._call_string_method(obj, method_name, args)
            raise InterpreterError(f"Cannot call method on {type(obj).__name__}")

        name_str = fn_name.name if isinstance(fn_name, Identifier) else fn_name

        if isinstance(name_str, str) and name_str in self.builtins:
            bn = self.builtins[name_str]
            if isinstance(bn, BuiltinFunction):
                return bn.call(args)

        fn = None
        if isinstance(fn_name, Identifier):
            fn = env.get(fn_name.name)

        if isinstance(fn, BuiltinFunction):
            return fn.call(args)
        if isinstance(fn, FunctionDef):
            return self.call_function(fn, args)
        if isinstance(fn, PuiClassDef):
            return self.call_class(fn, args)

        raise InterpreterError(f"'{name_str}' is not callable")

    def call_function(self, fn, args, self_obj=None):
        child_env = Env(fn.closure)
        if self_obj:
            child_env.define("self", self_obj)
        arg_idx = 0
        for param in fn.params:
            if self_obj and param.name == "self":
                continue
            if arg_idx < len(args):
                child_env.define(param.name, args[arg_idx])
                arg_idx += 1
            else:
                child_env.define(param.name, None)
        try:
            self.exec_block(fn.body, child_env)
            return None
        except ReturnOut as ret:
            return ret.value

    def call_class(self, cls, args):
        instance = PuiClassInstance(cls)
        if cls.init_method:
            self.call_function(cls.init_method, args, instance)
        return instance

    def _call_array_method(self, arr, method, args):
        if method == "push":
            arr.append(args[0])
            return None
        if method == "pop":
            return arr.pop()
        if method == "insert":
            arr.insert(int(args[0]), args[1])
            return None
        if method == "remove":
            arr.pop(int(args[0]))
            return None
        if method == "find":
            for i, item in enumerate(arr):
                if item == args[0]:
                    return i
            return -1
        if method == "contains":
            return args[0] in arr
        if method == "length":
            return len(arr)
        if method == "clear":
            arr.clear()
            return None
        raise InterpreterError(f"Array has no method '{method}'")

    def _call_string_method(self, s, method, args):
        if method == "length":
            return len(s)
        if method == "upper":
            return s.upper()
        if method == "lower":
            return s.lower()
        if method == "split":
            return s.split(args[0] if args else ",")
        if method == "strip":
            return s.strip()
        if method == "contains":
            return args[0] in s
        if method == "replace":
            return s.replace(args[0], args[1])
        if method == "find":
            return s.find(args[0])
        if method == "substring":
            start = int(args[0])
            end = int(args[1]) if len(args) > 1 else len(s)
            return s[start:end]
        raise InterpreterError(f"String has no method '{method}'")

    def eval_dot_access(self, node, env):
        obj = self.eval_expr(node.obj, env)
        if isinstance(obj, PuiClassInstance):
            v = obj.get(node.attr)
            if v is None:
                raise InterpreterError(f"'{obj.class_name}' has no attribute '{node.attr}'")
            return v
        if isinstance(obj, dict):
            return obj.get(node.attr, None)
        if isinstance(obj, list):
            if node.attr == "length":
                return len(obj)
        if isinstance(obj, str):
            return self._call_string_method(obj, node.attr, [])
        if isinstance(obj, PuiClassDef):
            if node.attr in obj.methods:
                return obj.methods[node.attr]
        raise InterpreterError(f"Cannot access '{node.attr}' on {type(obj).__name__}")

    def eval_index_access(self, node, env):
        obj = self.eval_expr(node.obj, env)
        idx = self.eval_expr(node.index, env)
        if isinstance(obj, list):
            return obj[int(idx)]
        if isinstance(obj, dict):
            return obj.get(idx, None)
        if isinstance(obj, str):
            return obj[int(idx)]
        raise InterpreterError(f"Cannot index into {type(obj).__name__}")


def is_truthy(val):
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, int):
        return val != 0
    if isinstance(val, float):
        return val != 0.0
    if isinstance(val, str):
        return len(val) > 0
    if isinstance(val, list):
        return len(val) > 0
    if isinstance(val, dict):
        return len(val) > 0
    return True


def execute(source):
    from compiler.parser import parse_source
    tree = parse_source(source)
    interp = Interpreter()
    interp.run(tree)
    return interp


def execute_file(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    return execute(source)