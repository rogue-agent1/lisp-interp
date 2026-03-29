from lisp_interp import run
assert run("(+ 1 2)") == [3]
assert run("(* 3 (+ 1 2))") == [9]
assert run("(if (> 3 2) 1 0)") == [1]
assert run("(begin (define x 10) (+ x 5))") == [15]
assert run("(begin (define sq (lambda (x) (* x x))) (sq 5))") == [25]
assert run("(car (list 1 2 3))") == [1]
assert run("(length (list 1 2 3))") == [3]
print("lisp_interp tests passed")
