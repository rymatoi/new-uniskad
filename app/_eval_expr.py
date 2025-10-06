import re
from collections.abc import Iterable
from contextlib import contextmanager
from contextvars import ContextVar

from sympy import (
    Add,
    Abs,
    And,
    Basic,
    Integer,
    Max,
    Min,
    Not,
    Or,
    Piecewise,
    Pow,
    S,
    sign,
    sympify,
)
from sympy.functions.elementary.integers import floor


def _sympify_value(value):
    if isinstance(value, Basic):
        return value
    return sympify(value)


def _flatten_sympy_args(value):
    if isinstance(value, Basic):
        yield value
        return

    if isinstance(value, (str, bytes)):
        yield _sympify_value(value)
        return

    if isinstance(value, Iterable):
        for item in value:
            yield from _flatten_sympy_args(item)
        return

    yield _sympify_value(value)


def _as_sympy_args(args):
    flattened = []
    for arg in args:
        flattened.extend(_flatten_sympy_args(arg))
    return flattened


_EVAL_CONTEXT = ContextVar('_eval_context', default={})


@contextmanager
def eval_context(**kwargs):
    current = _EVAL_CONTEXT.get().copy()
    current.update(kwargs)
    token = _EVAL_CONTEXT.set(current)
    try:
        yield
    finally:
        _EVAL_CONTEXT.reset(token)


def _get_eval_context():
    return _EVAL_CONTEXT.get()


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


def _func_range(*args):
    sympy_args = _as_sympy_args(args)
    if not sympy_args:
        raise ValueError('RANGE requires at least one argument')

    if len(sympy_args) == 1:
        start_expr = Integer(1)
        stop_expr = sympy_args[0]
        step_expr = Integer(1)
    elif len(sympy_args) == 2:
        start_expr, stop_expr = sympy_args
        step_expr = Integer(1)
    elif len(sympy_args) == 3:
        start_expr, stop_expr, step_expr = sympy_args
    else:
        raise ValueError('RANGE accepts up to three arguments')

    def _to_int(expr):
        if isinstance(expr, Basic):
            if not expr.is_integer:
                raise ValueError('RANGE arguments must be integers')
            return int(expr)
        if isinstance(expr, (int, float)):
            if isinstance(expr, float) and not expr.is_integer():
                raise ValueError('RANGE arguments must be integers')
            return int(expr)
        if isinstance(expr, str):
            if not expr.strip():
                raise ValueError('RANGE arguments must not be empty')
            return int(expr)
        raise ValueError('Unsupported RANGE argument type')

    start = _to_int(start_expr)
    stop = _to_int(stop_expr)
    step = _to_int(step_expr)

    if step == 0:
        raise ValueError('RANGE step must be non-zero')

    return list(range(start, stop, step))


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


def _func_column(identifier=None):
    context = _get_eval_context()
    columns = context.get('columns')
    if identifier is None:
        column_number = context.get('column_number')
        if column_number is None:
            raise ValueError('COLUMN is available only for table columns')
        return Integer(column_number)

    lookup = context.get('column_lookup') or {}

    value = identifier
    if isinstance(value, Basic):
        if value.is_number:
            if not value.is_integer:
                raise ValueError('COLUMN index must be an integer')
            idx = int(value)
            return Integer(idx)
        value = str(value)

    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            raise ValueError('COLUMN index must be an integer')
        idx = int(value)
        return Integer(idx)

    if not isinstance(value, str):
        value = str(value)

    stripped_value = value.strip()
    if stripped_value in lookup:
        return Integer(lookup[stripped_value])

    try:
        idx = int(stripped_value)
    except ValueError as exc:
        raise ValueError(f'Unknown column reference: {value}') from exc

    if columns is not None and (idx < 1 or idx > len(columns)):
        raise ValueError('COLUMN index is out of range')

    return Integer(idx)


CUSTOM_FUNCTIONS = {
    'СУММ': _func_summ,
    'СРЗНАЧ': _func_average,
    'МАКС': _func_max,
    'МИН': _func_min,
    'СЧЁТ': _func_count,
    'СЧЕТ': _func_count_alias,
    'RANGE': _func_range,
    'Range': _func_range,
    'ДИАПАЗОН': _func_range,
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
    'COLUMN': _func_column,
    'СТОЛБЕЦ': _func_column,
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
        parsed = sympify(expr, locals=CUSTOM_FUNCTIONS)
    except Exception:
        return expr

    if isinstance(parsed, Basic):
        try:
            return parsed.evalf()
        except Exception:
            return expr

    return parsed


if __name__ == '__main__':
    print(chr(sum(range(ord(min(str(not ())))))))
