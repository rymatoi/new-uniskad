from app.plugins.project.data.datamanagers.epure_datamanager import EpureDataManager
from app.plugins.project.services.coordinates import ItemProcessor
from app.plugins.project.services.data_processors.base_dp import DataProcessor
from app.plugins.project.services.data_processors.test_dp import TestProcessor
from app.plugins.project.utils.converters.epure_converter import EpureConverter


class EpureProcessor(DataProcessor):
    DATA_MANAGER = EpureDataManager

    def __init__(self, item):
        super().__init__(item)
        self.test_nodes = self.load_test_nodes(item)
        self.epure_data = self.init_epure_data(item)

    def init_epure_data(self, item):
        """Оптимизированная обработка данных для эпюр"""
        item.param_list = EpureConverter.get_param_list(item)
        test_id_list = self.test_nodes.keys()
        return self.data_manager.get_epure_data(test_id_list, item.param_list)

    @staticmethod
    def load_test_nodes(item):
        return TestProcessor.collect_tests(item)

    def get_epure_curves(self):
        return ItemProcessor.get_epure_data(self.epure_data, self.test_nodes)
