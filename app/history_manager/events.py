from app.history_manager.history_manager import Event


class LegendPositionChangeEvent(Event):

    def __init__(self, item, old_value, new_value):
        super().__init__(item)
        self.old_value = old_value
        self.new_value = new_value

    def undo(self):
        self._item.update_pos(self.new_value)

    def redo(self):
        self._item.update_pos(self.old_value)


class RowPropUpdateEvent(Event):

    def __init__(self, item, prop_name, old_value, new_value):
        super().__init__(item)
        self.prop_name = prop_name
        self.old_value = old_value
        self.new_value = new_value

    def undo(self):
        self._item.update(self.prop_name, self.new_value)

    def redo(self):
        self._item.update_pos(self.prop_name, self.old_value)
