import sys, argparse, re

def tokenize(s):
    return s.replace("(", " ( ").replace(")", " ) ").split()

def parse(tokens):
    if not tokens: raise SyntaxError("unexpected EOF")
    t = tokens.pop(0)
    if t == "(":
        lst = []
        while tokens[0] != ")": lst.append(parse(tokens))
        tokens.pop(0)
        return lst
    elif t == ")": raise SyntaxError("unexpected )")
    else:
        try: return int(t)
        except ValueError:
            try: return float(t)
            except ValueError: return t

def env_default():
    import operator as op
    e = {"+": op.add, "-": op.sub, "*": op.mul, "/": op.truediv,
         "=": op.eq, "<": op.lt, ">": op.gt, "<=": op.le, ">=": op.ge,
         "not": lambda x: not x, "car": lambda x: x[0], "cdr": lambda x: x[1:],
         "cons": lambda x, y: [x] + y, "list": lambda *x: list(x),
         "len": len, "null?": lambda x: x == [], "number?": lambda x: isinstance(x, (int, float)),
         "print": lambda x: print(x) or x, "#t": True, "#f": False, "nil": []}
    return e

def evaluate(x, env):
    if isinstance(x, str): return env[x]
    if not isinstance(x, list): return x
    if x[0] == "quote": return x[1]
    if x[0] == "if": return evaluate(x[2] if evaluate(x[1], env) else x[3], env)
    if x[0] == "define": env[x[1]] = evaluate(x[2], env); return None
    if x[0] == "lambda":
        params, body = x[1], x[2]
        return lambda *args: evaluate(body, {**env, **dict(zip(params, args))})
    if x[0] == "begin":
        for exp in x[1:]: val = evaluate(exp, env)
        return val
    proc = evaluate(x[0], env)
    args = [evaluate(a, env) for a in x[1:]]
    return proc(*args)

def main():
    p = argparse.ArgumentParser(description="Lisp interpreter")
    p.add_argument("file", nargs="?")
    p.add_argument("-c", "--code")
    p.add_argument("--repl", action="store_true")
    args = p.parse_args()
    env = env_default()
    if args.code:
        r = evaluate(parse(tokenize(args.code)), env)
        if r is not None: print(r)
    elif args.file:
        code = open(args.file).read()
        for expr in re.findall(r"\([^()]*(?:\([^()]*\)[^()]*)*\)", code):
            r = evaluate(parse(tokenize(expr)), env)
            if r is not None: print(r)
    elif args.repl:
        while True:
            try:
                line = input("lisp> ")
                r = evaluate(parse(tokenize(line)), env)
                if r is not None: print(r)
            except (EOFError, KeyboardInterrupt): break
            except Exception as e: print(f"Error: {e}")
    else: p.print_help()

if __name__ == "__main__":
    main()
