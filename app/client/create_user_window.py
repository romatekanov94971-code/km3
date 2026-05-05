from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.client.api_client import ApiClient


class CreateUserWindow(QDialog):
    """Административное окно создания пользователей и администраторов."""

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.setWindowTitle("Создание пользователя")
        self.setMinimumWidth(430)

        self.info = QLabel("Создайте учетную запись. По умолчанию пользователь обязан сменить первичный пароль.")
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.repeat_password = QLineEdit()
        self.repeat_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.role = QComboBox()
        self.role.addItems(["user", "admin"])

        self.must_change_password = QCheckBox("Требовать смену пароля при первом входе")
        self.must_change_password.setChecked(True)

        form = QFormLayout()
        form.addRow("Логин", self.username)
        form.addRow("Пароль", self.password)
        form.addRow("Повтор пароля", self.repeat_password)
        form.addRow("Роль", self.role)
        form.addRow("", self.must_change_password)

        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.create_user)

        layout = QVBoxLayout()
        layout.addWidget(self.info)
        layout.addLayout(form)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def create_user(self) -> None:
        username = self.username.text().strip()
        password = self.password.text()
        repeat = self.repeat_password.text()
        role = self.role.currentText()

        if not username or not password or not repeat:
            QMessageBox.warning(self, "Проверка", "Заполните логин, пароль и повтор пароля.")
            return
        if password != repeat:
            QMessageBox.warning(self, "Проверка", "Пароль и повтор пароля не совпадают.")
            return

        try:
            result = self.api.create_user(
                username=username,
                password=password,
                role=role,
                must_change_password=self.must_change_password.isChecked(),
            )
            QMessageBox.information(
                self,
                "Пользователь создан",
                f"Создана учетная запись: {result['username']}\nРоль: {result['role']}",
            )
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка создания пользователя", str(exc))
