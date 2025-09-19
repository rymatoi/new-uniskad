from app.plugins.project.utils.collectors import PlotDataCollector as Collector
from db import sp  # предположим, что это модуль работы с БД


class EpureDataManager:
    def __init__(self, project_id):
        self.project_id = project_id

    def get_epure_data(self, test_ids, param):
        """Получение данных кривых из БД"""
        return Collector.collect_epure_values(sp.get_epure_data(
            test_ids,
            param
        ))
