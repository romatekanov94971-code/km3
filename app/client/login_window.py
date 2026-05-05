from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.client.api_client import ApiClient
from app.client.change_password_window import ChangePasswordWindow


class LoginWindow(QDialog):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.setWindowTitle("Вход в систему")
        self.setMinimumWidth(360)

        self.username = QLineEdit("admin")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.status = QLabel("Введите имя пользователя и пароль.")
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self._login)

        form = QFormLayout()
        form.addRow("Пользователь", self.username)
        form.addRow("Пароль", self.password)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addLayout(form)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def _login(self) -> None:
        try:
            result = self.api.login(self.username.text().strip(), self.password.text())
            if result.get("must_change_password"):
                change_dialog = ChangePasswordWindow(
                    self.api,
                    old_password_hint=self.password.text(),
                    forced=True,
                )
                if change_dialog.exec() != change_dialog.DialogCode.Accepted:
                    self.status.setText("Сначала смените первичный пароль")
                    return
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка входа", str(exc))
