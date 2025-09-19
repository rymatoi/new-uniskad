import sys


class Event:
    def __init__(self, item):
        self._item = item

    def undo(self):
        pass

    def redo(self):
        pass


class EventStack:
    _history: list
    _history_position: int

    def __init__(self):
        self._history = []
        self._history_position = 0

    @property
    def history(self):
        return self._history

    def undo(self):
        if self._history_position > 0:
            self._history_position -= 1

            self._history[self._history_position].undo()
        else:
            print('nothing to undo')

    def redo(self):
        if self._history_position + 1 < len(self._history):
            self._history_position += 1
            self._history[self._history_position].redo()

    def add_event(self, event):
        if len(self._history) == self._history_position:
            self._history.append(event)
            self._history_position += 1

        else:
            self._history = self._history[:self._history_position]
            self._history_position += 1
            self._history.append(event)
