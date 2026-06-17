from app.plugins.project.core.exceptions import InvalidCurveDataError


class GraphConverter(object):
    @staticmethod
    def str_to_float(val):
        if val is None:
            raise InvalidCurveDataError("Cannot convert None to float")

        if isinstance(val, str):
            val = val.strip()
            if not val:
                raise InvalidCurveDataError("Cannot convert empty string to float")
            val = val.replace(',', '.', 1)

        try:
            return float(val)
        except (TypeError, ValueError) as exc:
            raise InvalidCurveDataError(f"Cannot convert to float: {val!r}") from exc
