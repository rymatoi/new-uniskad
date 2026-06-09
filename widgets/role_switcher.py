"""Reusable control for switching the active application role."""

from PySide2.QtWidgets import QHBoxLayout, QMenu, QToolButton, QWidget


class RoleSwitcherWidget(QWidget):
    """Display the current role and delegate role changes to a controller."""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

        self.button = QToolButton(self)
        self.button.setObjectName("role_switcher_button")
        self.button.setPopupMode(QToolButton.MenuButtonPopup)
        self.button.setMenu(self._create_menu())

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)
        layout.addStretch()

        self.refresh()

    def _create_menu(self):
        menu = QMenu(self.button)
        for role in self.controller.roles:
            action = menu.addAction(role.rolename)
            action.triggered.connect(
                lambda checked=False, role_name=role.name: self._change_role(role_name)
            )
        return menu

    def _change_role(self, role_name):
        self.controller.change_role(role_name)
        self.refresh()

    def refresh(self):
        """Refresh the displayed role from the controller's current state."""
        current_role = self.controller.current_role
        self.button.setText(current_role.rolename)


__all__ = ["RoleSwitcherWidget"]
