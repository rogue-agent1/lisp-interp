#!/usr/bin/env python3
"""Minimal Lisp interpreter — parse, eval, lambdas, let."""
import sys, re

def tokenize(s):
    return s.replace("(", " ( ").replace(")", " ) ").split()

def parse(tokens):
    if not tokens: raise SyntaxError("Unexpected EOF")
    t = tokens.pop(0)
    if t == "(":
        lst = []
        while tokens[0] != ")":
            lst.append(parse(tokens))
        tokens.pop(0)
        return lst
    elif t == ")":
        raise SyntaxError("Unexpected )")
    else:
        try: return int(t)
        except ValueError:
            try: return float(t)
            except ValueError: return t

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer
    def find(self, key):
        if key in self: return self
        if self.outer: return self.outer.find(key)
        raise NameError(f"Undefined: {key}")

def standard_env():
    env = Env()
    import operator, math
    env.update({"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv,
                "=": operator.eq, "<": operator.lt, ">": operator.gt,
                "car": lambda x: x[0], "cdr": lambda x: x[1:], "cons": lambda x,y: [x]+y,
                "list": lambda *x: list(x), "null?": lambda x: x == [],
                "abs": abs, "min": min, "max": max, "not": lambda x: not x,
                "pi": math.pi, "#t": True, "#f": False})
    return env

def eval_expr(x, env):
    if isinstance(x, str):
        return env.find(x)[x]
    elif not isinstance(x, list):
        return x
    elif x[0] == "quote":
        return x[1]
    elif x[0] == "if":
        _, test, conseq, alt = x
        return eval_expr(conseq if eval_expr(test, env) else alt, env)
    elif x[0] == "define":
        env[x[1]] = eval_expr(x[2], env)
    elif x[0] == "lambda":
        _, params, body = x
        return lambda *args: eval_expr(body, Env(params, args, env))
    elif x[0] == "let":
        bindings, body = x[1], x[2]
        inner = Env(outer=env)
        for name, expr in bindings:
            inner[name] = eval_expr(expr, env)
        return eval_expr(body, inner)
    elif x[0] == "begin":
        val = None
        for expr in x[1:]:
            val = eval_expr(expr, env)
        return val
    else:
        fn = eval_expr(x[0], env)
        args = [eval_expr(a, env) for a in x[1:]]
        return fn(*args)

def run(code):
    env = standard_env()
    tokens = tokenize(code)
    results = []
    while tokens:
        expr = parse(tokens)
        r = eval_expr(expr, env)
        if r is not None:
            results.append(r)
    return results, env

def test():
    r, _ = run("(+ 1 2)")
    assert r == [3]
    r, _ = run("(define x 10) (+ x 5)")
    assert r == [15]
    r, _ = run("(if (> 3 2) 1 0)")
    assert r == [1]
    r, _ = run("((lambda (x y) (+ x y)) 3 4)")
    assert r == [7]
    r, _ = run("(let ((a 5) (b 3)) (+ a b))")
    assert r == [8]
    r, _ = run("(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))(fact 5)")
    assert r == [120]
    print("  lisp_interp: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Minimal Lisp interpreter")
