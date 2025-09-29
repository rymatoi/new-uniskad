from sympy import *


def _as_sympy_args(args):
    return [sympify(arg) if not isinstance(arg, Basic) else arg for arg in args]


def СУММ(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Add(*sympy_args)


def СРЗНАЧ(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Add(*sympy_args) / Integer(len(sympy_args))


def МАКС(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Max(*sympy_args)


def МИН(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Min(*sympy_args)


def СЧЁТ(*args):
    sympy_args = _as_sympy_args(args)
    return Integer(len(sympy_args))


def СЧЕТ(*args):
    return СЧЁТ(*args)


def ЕСЛИ(condition, true_value, false_value=0):
    condition_expr = sympify(condition) if not isinstance(condition, Basic) else condition
    true_expr = sympify(true_value) if not isinstance(true_value, Basic) else true_value
    false_expr = sympify(false_value) if not isinstance(false_value, Basic) else false_value
    return Piecewise((true_expr, condition_expr), (false_expr, True))


CUSTOM_FUNCTIONS = {
    'СУММ': СУММ,
    'СРЗНАЧ': СРЗНАЧ,
    'МАКС': МАКС,
    'МИН': МИН,
    'СЧЁТ': СЧЁТ,
    'СЧЕТ': СЧЕТ,
    'ЕСЛИ': ЕСЛИ,
}


def eval_expr(expr: str) -> "Optional[float]":
    """Вычисление выражения"""
    expr = expr.replace(';', ',')
    expr = expr.replace(',', '.')
    try:
        return sympify(expr, locals=CUSTOM_FUNCTIONS).evalf()
    except Exception as ex:
        return expr


if __name__ == '__main__':
    print(chr(sum(range(ord(min(str(not ())))))))
