import re

from sympy import Max, Min, Abs, Float, sympify, sin, cos


def _sum(*args):
    return sum(args)


def _average(*args):
    if not args:
        return Float(0)
    return _sum(*args) / len(args)


def _if(condition, true_value, false_value):
    try:
        return true_value if float(condition) != 0 else false_value
    except Exception:
        return true_value if bool(condition) else false_value


def _round(value, digits=0):
    try:
        digits = int(digits)
    except Exception:
        digits = 0
    try:
        return Float(round(float(value), digits))
    except Exception:
        return value


ALLOWED_FUNCTIONS = {
    'SUM': _sum,
    'sum': _sum,
    'AVERAGE': _average,
    'average': _average,
    'AVG': _average,
    'avg': _average,
    'MIN': Min,
    'min': Min,
    'MAX': Max,
    'max': Max,
    'ABS': Abs,
    'abs': Abs,
    'IF': _if,
    'if': _if,
    'ROUND': _round,
    'round': _round,
    'SIN': sin,
    'sin': sin,
    'COS': cos,
    'cos': cos,
}


def eval_expr(expr: str) -> "Optional[float]":
    """Вычисление выражения"""
    if not isinstance(expr, str):
        expr = str(expr)

    expr = expr.replace(';', ',')
    expr = re.sub(r'(?<=\d),(?=\d)', '.', expr)

    try:
        evaluated = sympify(expr, locals=ALLOWED_FUNCTIONS)
        result = evaluated.evalf()
        return result
    except Exception:
        return expr


if __name__ == '__main__':
    print(chr(sum(range(ord(min(str(not ())))))))
