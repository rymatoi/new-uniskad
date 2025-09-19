from app.plugins.project.core.exceptions import EpureAttributeError


class EpureConverter(object):
    @staticmethod
    def get_param_list(item):
        if not hasattr(item, 'param_list'):
            raise EpureAttributeError
        if isinstance(item.param_list, str):
            return [p.strip("' ") for p in item.param_list.strip("[]").split(",")]
        return item.param_list
