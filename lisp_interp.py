#!/usr/bin/env python3
"""Minimal Lisp interpreter. Zero dependencies."""
import math, operator

def tokenize(s):
    return s.replace("(", " ( ").replace(")", " ) ").split()

def parse(tokens):
    if not tokens: raise SyntaxError("Unexpected EOF")
    token = tokens.pop(0)
    if token == "(":
        lst = []
        while tokens[0] != ")": lst.append(parse(tokens))
        tokens.pop(0)
        return lst
    elif token == ")": raise SyntaxError("Unexpected )")
    else:
        try: return int(token)
        except ValueError:
            try: return float(token)
            except ValueError: return token

def standard_env():
    env = {
        "+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv,
        ">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le, "=": operator.eq,
        "abs": abs, "max": max, "min": min, "not": operator.not_,
        "list": lambda *x: list(x), "car": lambda x: x[0], "cdr": lambda x: x[1:],
        "cons": lambda x, y: [x] + list(y), "length": len, "null?": lambda x: x == [],
        "number?": lambda x: isinstance(x, (int, float)), "symbol?": lambda x: isinstance(x, str),
        "pi": math.pi, "sqrt": math.sqrt,
    }
    return env

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args)); self.outer = outer
    def find(self, var):
        if var in self: return self
        if self.outer: return self.outer.find(var)
        raise NameError(var)

def eval_lisp(x, env):
    if isinstance(x, str): return env.find(x)[x]
    elif not isinstance(x, list): return x
    elif x[0] == "quote": return x[1]
    elif x[0] == "if":
        _, test, conseq = x[:3]; alt = x[3] if len(x) > 3 else None
        return eval_lisp(conseq if eval_lisp(test, env) else alt, env)
    elif x[0] == "define":
        _, var, expr = x; env[var] = eval_lisp(expr, env)
    elif x[0] == "lambda":
        _, params, body = x
        return lambda *args: eval_lisp(body, Env(params, args, env))
    elif x[0] == "begin":
        val = None
        for expr in x[1:]: val = eval_lisp(expr, env)
        return val
    else:
        proc = eval_lisp(x[0], env)
        args = [eval_lisp(a, env) for a in x[1:]]
        return proc(*args)

def run(program):
    env = Env(outer=None); env.update(standard_env())
    tokens = tokenize(program)
    results = []
    while tokens:
        expr = parse(tokens)
        result = eval_lisp(expr, env)
        if result is not None: results.append(result)
    return results

if __name__ == "__main__":
    import sys
    code = " ".join(sys.argv[1:]) or "(+ 1 2)"
    print(run(code))
