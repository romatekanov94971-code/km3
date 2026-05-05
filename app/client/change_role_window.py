from __future__ import annotations

from PyQt6.QtWidgets import QComboBox, QDialog, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.client.api_client import ApiClient


class ChangeRoleWindow(QDialog):
    """Административное окно изменения прав доступа пользователя."""

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.setWindowTitle("Изменение роли пользователя")
        self.setMinimumWidth(420)

        self.username = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(["user", "admin"])

        form = QFormLayout()
        form.addRow("Логин пользователя", self.username)
        form.addRow("Новая роль", self.role)

        self.change_button = QPushButton("Изменить роль")
        self.change_button.clicked.connect(self.change_role)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.change_button)
        self.setLayout(layout)

    def change_role(self) -> None:
        username = self.username.text().strip()
        if not username:
            QMessageBox.warning(self, "Проверка", "Укажите логин пользователя.")
            return

        try:
            result = self.api.change_user_role(username, self.role.currentText())
            QMessageBox.information(
                self,
                "Роль изменена",
                f"Пользователь: {result['username']}\nНовая роль: {result['role']}",
            )
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка изменения роли", str(exc))
