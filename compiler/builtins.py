import math
import time
import sys


class BuiltinFunction:
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def call(self, args):
        return self.fn(args)

    def __repr__(self):
        return f"<builtin {self.name}>"


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


def builtin_print(args):
    parts = []
    for a in args:
        parts.append(to_string(a))
    print(" ".join(parts))
    return None


def builtin_range_fn(args):
    if len(args) == 1:
        return list(range(int(args[0])))
    elif len(args) == 2:
        return list(range(int(args[0]), int(args[1])))
    elif len(args) == 3:
        return list(range(int(args[0]), int(args[1]), int(args[2])))
    return []


def builtin_len(args):
    val = args[0]
    if isinstance(val, str):
        return len(val)
    if isinstance(val, list):
        return len(val)
    if isinstance(val, dict):
        return len(val)
    return 0


def builtin_typeof(args):
    val = args[0]
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "bool"
    if isinstance(val, int):
        return "int"
    if isinstance(val, float):
        return "float"
    if isinstance(val, str):
        return "string"
    if isinstance(val, list):
        return "array"
    if isinstance(val, dict):
        return "dict"
    if isinstance(val, FunctionDef):
        return "function"
    if isinstance(val, BuiltinFunction):
        return "builtin"
    if isinstance(val, PuiClassInstance):
        return val.class_name
    return "unknown"


def builtin_int(args):
    return int(args[0])


def builtin_float(args):
    return float(args[0])


def builtin_str(args):
    return to_string(args[0])


def builtin_abs(args):
    return abs(args[0])


def builtin_min_fn(args):
    vals = args[0] if len(args) == 1 and isinstance(args[0], list) else args
    return min(vals)


def builtin_max_fn(args):
    vals = args[0] if len(args) == 1 and isinstance(args[0], list) else args
    return max(vals)


def builtin_clamp(args):
    val, lo, hi = args[0], args[1], args[2]
    return max(lo, min(hi, val))


def builtin_floor(args):
    return math.floor(args[0])


def builtin_ceil(args):
    return math.ceil(args[0])


def builtin_round_val(args):
    return round(args[0])


def builtin_sqrt(args):
    return math.sqrt(args[0])


def builtin_sin(args):
    return math.sin(args[0])


def builtin_cos(args):
    return math.cos(args[0])


def builtin_tan(args):
    return math.tan(args[0])


def builtin_random_fn(args):
    import random
    if len(args) == 0:
        return random.random()
    elif len(args) == 1:
        return random.randint(0, int(args[0]) - 1)
    elif len(args) == 2:
        return random.randint(int(args[0]), int(args[1]))
    return 0


def builtin_append(args):
    args[0].append(args[1])
    return None


def builtin_remove_at(args):
    args[0].pop(int(args[1]))
    return None


def builtin_insert(args):
    args[0].insert(int(args[1]), args[2])
    return None


def builtin_slice(args):
    arr = args[0]
    start = int(args[1]) if len(args) > 1 else 0
    end = int(args[2]) if len(args) > 2 else len(arr)
    return arr[start:end]


def builtin_keys(args):
    return list(args[0].keys())


def builtin_values(args):
    return list(args[0].values())


def builtin_has(args):
    return args[0].get(args[1], None) is not None or args[1] in args[0]


def builtin_time_now(args):
    return time.time()


def builtin_time_sleep(args):
    time.sleep(args[0])


def builtin_type(args):
    val = args[0]
    if isinstance(val, list):
        if len(args) > 1:
            return isinstance(val[0], type(args[1]))
        return True
    return False


def to_string(val):
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return str(val)
    if isinstance(val, list):
        parts = []
        for item in val:
            parts.append(to_string(item))
        return "[" + ", ".join(parts) + "]"
    if isinstance(val, dict):
        parts = []
        for k, v in val.items():
            parts.append(f"{to_string(k)}: {to_string(v)}")
        return "{" + ", ".join(parts) + "}"
    return str(val)


class FunctionDef:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure

    def __repr__(self):
        return f"<function {self.name}>"


class PuiClassDef:
    def __init__(self, name, parent, methods, init_method):
        self.name = name
        self.parent = parent
        self.methods = methods
        self.init_method = init_method

    def __repr__(self):
        return f"<class {self.name}>"


class PuiClassInstance:
    def __init__(self, class_def):
        self.class_name = class_def.name
        self.fields = {}
        self._class = class_def

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        if name in self._class.methods:
            return self._class.methods[name]
        if self._class.parent:
            p = self._class.parent
            while p:
                if name in p.methods:
                    return p.methods[name]
                p = p.parent
        return None

    def set(self, name, value):
        self.fields[name] = value

    def __repr__(self):
        return f"<{self.class_name} instance>"


def get_default_builtins():
    builtins = {
        "print": BuiltinFunction("print", builtin_print),
        "range": BuiltinFunction("range", builtin_range_fn),
        "len": BuiltinFunction("len", builtin_len),
        "typeof": BuiltinFunction("typeof", builtin_typeof),
        "int": BuiltinFunction("int", builtin_int),
        "float": BuiltinFunction("float", builtin_float),
        "str": BuiltinFunction("str", builtin_str),
        "abs": BuiltinFunction("abs", builtin_abs),
        "min": BuiltinFunction("min", builtin_min_fn),
        "max": BuiltinFunction("max", builtin_max_fn),
        "clamp": BuiltinFunction("clamp", builtin_clamp),
        "floor": BuiltinFunction("floor", builtin_floor),
        "ceil": BuiltinFunction("ceil", builtin_ceil),
        "round": BuiltinFunction("round", builtin_round_val),
        "sqrt": BuiltinFunction("sqrt", builtin_sqrt),
        "sin": BuiltinFunction("sin", builtin_sin),
        "cos": BuiltinFunction("cos", builtin_cos),
        "tan": BuiltinFunction("tan", builtin_tan),
        "random": BuiltinFunction("random", builtin_random_fn),
        "append": BuiltinFunction("append", builtin_append),
        "remove": BuiltinFunction("remove", builtin_remove_at),
        "insert": BuiltinFunction("insert", builtin_insert),
        "slice": BuiltinFunction("slice", builtin_slice),
        "keys": BuiltinFunction("keys", builtin_keys),
        "values": BuiltinFunction("values", builtin_values),
        "has": BuiltinFunction("has", builtin_has),
        "time": BuiltinFunction("time", builtin_time_now),
        "sleep": BuiltinFunction("sleep", builtin_time_sleep),
    }
    builtins["PI"] = math.pi
    builtins["TAU"] = math.tau
    builtins["INF"] = float("inf")
    return builtins