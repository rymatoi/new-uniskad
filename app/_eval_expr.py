import re

from sympy import Add, Basic, Integer, Max, Min, Piecewise, sympify


def _as_sympy_args(args):
    return [sympify(arg) if not isinstance(arg, Basic) else arg for arg in args]


def _func_summ(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Add(*sympy_args)


def _func_average(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Add(*sympy_args) / Integer(len(sympy_args))


def _func_max(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Max(*sympy_args)


def _func_min(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return Integer(0)
    return Min(*sympy_args)


def _func_count(*args):
    sympy_args = _as_sympy_args(args)
    return Integer(len(sympy_args))


def _func_count_alias(*args):
    return _func_count(*args)


def _func_if(condition, true_value, false_value=0):
    condition_expr = sympify(condition) if not isinstance(condition, Basic) else condition
    true_expr = sympify(true_value) if not isinstance(true_value, Basic) else true_value
    false_expr = sympify(false_value) if not isinstance(false_value, Basic) else false_value
    return Piecewise((true_expr, condition_expr), (false_expr, True))


CUSTOM_FUNCTIONS = {
    'СУММ': _func_summ,
    'СРЗНАЧ': _func_average,
    'МАКС': _func_max,
    'МИН': _func_min,
    'СЧЁТ': _func_count,
    'СЧЕТ': _func_count_alias,
    'ЕСЛИ': _func_if,
}


def eval_expr(expr: str) -> "Optional[float]":
    """Вычисление выражения"""
    expr = expr.replace(';', ',')
    # Excel использует запятую как десятичный разделитель. Заменяем только те
    # запятые, которые стоят между цифрами, чтобы аргументные запятые не
    # превращались в точки.
    expr = re.sub(r'(?<=\d),(?=\d)', '.', expr)
    try:
        return sympify(expr, locals=CUSTOM_FUNCTIONS).evalf()
    except Exception as ex:
        return expr


if __name__ == '__main__':
    print(chr(sum(range(ord(min(str(not ())))))))
