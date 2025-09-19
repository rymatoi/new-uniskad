from app.plugins.project.services.coordinates import ItemProcessor
from app.plugins.project.services.data_processors.test_dp import TestProcessor


class DataProcessor:
    DATA_MANAGER = None

    def __init__(self, item):
        self._data_manager = self.init_data_manager(item)

    @property
    def data_manager(self):
        if self._data_manager is None:
            raise Exception('DataProcessor was not initialized')  # TODO добавить кастомный эксепшн
        else:
            return self._data_manager

    def init_data_manager(self, item):
        if self.DATA_MANAGER is not None:
            return self.DATA_MANAGER(ItemProcessor.get_item_id(item))
