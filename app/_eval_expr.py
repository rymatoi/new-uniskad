import re

from sympy import Add, Abs, And, Basic, Integer, Max, Min, Not, Or, Piecewise, Pow, S, sign, sympify
from sympy.functions.elementary.integers import floor


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


def _func_abs(value):
    value_expr = sympify(value) if not isinstance(value, Basic) else value
    return Abs(value_expr)


def _func_power(base, exponent):
    base_expr = sympify(base) if not isinstance(base, Basic) else base
    exponent_expr = sympify(exponent) if not isinstance(exponent, Basic) else exponent
    return Pow(base_expr, exponent_expr)


def _func_round(value, digits=0):
    value_expr = sympify(value) if not isinstance(value, Basic) else value
    digits_expr = sympify(digits) if not isinstance(digits, Basic) else digits

    if not digits_expr.is_integer:
        raise ValueError('ROUND requires an integer number of digits')

    factor = Pow(Integer(10), digits_expr)
    scaled = Abs(value_expr) * factor
    rounded = floor(scaled + S.Half)
    return sign(value_expr) * rounded / factor


def _func_and(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return S.true
    return And(*sympy_args)


def _func_or(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        return S.false
    return Or(*sympy_args)


def _func_not(value):
    value_expr = sympify(value) if not isinstance(value, Basic) else value
    return Not(value_expr)


CUSTOM_FUNCTIONS = {
    'СУММ': _func_summ,
    'СРЗНАЧ': _func_average,
    'МАКС': _func_max,
    'МИН': _func_min,
    'СЧЁТ': _func_count,
    'СЧЕТ': _func_count_alias,
    'ЕСЛИ': _func_if,
    'ABS': _func_abs,
    'МОДУЛЬ': _func_abs,
    'POWER': _func_power,
    'СТЕПЕНЬ': _func_power,
    'ROUND': _func_round,
    'ОКРУГЛ': _func_round,
    'AND': _func_and,
    'И': _func_and,
    'OR': _func_or,
    'ИЛИ': _func_or,
    'NOT': _func_not,
    'НЕ': _func_not,
}


def eval_expr(expr: str) -> "Optional[float]":
    """Вычисление выражения"""
    expr = expr.replace(';', ',')
    # Excel использует запятую как десятичный разделитель. Заменяем только те
    # запятые, которые формируют число (нет точки непосредственно слева), чтобы
    # аргументные разделители, появившиеся после замены `;` на `,`, не
    # превращались в точки.
    expr = re.sub(r'(?<!\.)\b(\d+),(\d+)\b', r'\1.\2', expr)
    try:
        return sympify(expr, locals=CUSTOM_FUNCTIONS).evalf()
    except Exception as ex:
        return expr


if __name__ == '__main__':
    print(chr(sum(range(ord(min(str(not ())))))))
