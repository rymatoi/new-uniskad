from sympy import *


def eval_expr(expr: str) -> "Optional[float]":
    """Вычисление выражения"""
    expr = expr.replace(',', '.')
    try:
        return sympify(expr).evalf()
    except Exception as ex:
        return expr


if __name__ == '__main__':
    print(chr(sum(range(ord(min(str(not ())))))))
