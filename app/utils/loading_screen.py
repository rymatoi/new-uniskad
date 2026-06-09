from PySide2.QtCore import QThread, Signal, Qt, QRunnable, Slot, QObject
from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel


class DatabaseWorker(QThread):
    # Do not shadow QThread.finished with a result-bearing signal. Consumers
    # may safely use the inherited signal to dispose of this object.
    result_ready = Signal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.res = None

    def run(self):
        # Выполняем переданную функцию с аргументами
        result = self.func(*self.args, **self.kwargs)
        self.result_ready.emit(result)
        self.res = result


class Worker(QRunnable):
    '''
    Worker thread
    '''

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.res = None
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except:
            print('error')
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
        # self.finished.emit(result)
        # self.res = result


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)


class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Загрузка..")
        self.setModal(True)
        self.label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedWidth(100)
        self.setFixedWidth(200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def update_label_text(self):
        self.loading_dialog.label.setText('Завершено')
