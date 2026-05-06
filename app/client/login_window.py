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
        self.setWindowTitle("Вход в Energy System")
        self.setMinimumWidth(430)

        title = QLabel("Energy System")
        title.setProperty("role", "title")
        subtitle = QLabel("Оценка эффективности энергооборудования ТЭС")
        subtitle.setProperty("role", "subtitle")

        self.username = QLineEdit("admin")
        self.username.setPlaceholderText("Введите логин")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Введите пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.returnPressed.connect(self._login)

        self.status = QLabel("Введите учетные данные для входа.")
        self.status.setProperty("role", "subtitle")
        self.status.setWordWrap(True)

        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("primaryButton")
        self.login_button.clicked.connect(self._login)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Пользователь", self.username)
        form.addRow("Пароль", self.password)

        hint = QLabel(
            "Первичный пароль администратора задается через ENERGY_DEFAULT_ADMIN_PASSWORD "
            "или генерируется в data/initial_admin_credentials.txt."
        )
        hint.setProperty("role", "subtitle")
        hint.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(self.status)
        layout.addLayout(form)
        layout.addWidget(self.login_button)
        layout.addWidget(hint)
        self.setLayout(layout)

    def _login(self) -> None:
        self.login_button.setEnabled(False)
        self.status.setText("Проверка учетных данных...")
        try:
            result = self.api.login(self.username.text().strip(), self.password.text())
            if result.get("must_change_password"):
                change_dialog = ChangePasswordWindow(
                    self.api,
                    old_password_hint=self.password.text(),
                    forced=True,
                )
                if change_dialog.exec() != change_dialog.DialogCode.Accepted:
                    self.status.setText("Сначала смените первичный пароль.")
                    return
            self.accept()
        except Exception as exc:
            self.status.setText("Не удалось войти.")
            QMessageBox.critical(self, "Ошибка входа", str(exc))
        finally:
            self.login_button.setEnabled(True)


__all__ = ["LoginWindow"]
