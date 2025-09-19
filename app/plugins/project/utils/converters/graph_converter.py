from app.plugins.project.core.exceptions import InvalidCurveDataError


class GraphConverter(object):
    @staticmethod
    def str_to_float(val):
        try:
            if val is None:
                raise InvalidCurveDataError
            return float(val)
        except ValueError:
            raise InvalidCurveDataError
