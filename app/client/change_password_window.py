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


class ChangePasswordWindow(QDialog):
    """Окно смены пароля пользователя."""

    def __init__(self, api: ApiClient, old_password_hint: str = "", forced: bool = False) -> None:
        super().__init__()
        self.api = api
        self.forced = forced
        self.setWindowTitle("Смена пароля")
        self.setMinimumWidth(460)

        title = QLabel("Смена пароля")
        title.setProperty("role", "title")
        hint_text = (
            "Необходимо сменить пароль после первичной аутентификации."
            if forced
            else "Введите старый пароль и новый пароль."
        )
        self.status = QLabel(hint_text)
        self.status.setProperty("role", "subtitle")
        self.status.setWordWrap(True)

        self.old_password = QLineEdit(old_password_hint)
        self.old_password.setPlaceholderText("Старый пароль")
        self.old_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Новый пароль")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.repeat_password = QLineEdit()
        self.repeat_password.setPlaceholderText("Повторите новый пароль")
        self.repeat_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.repeat_password.returnPressed.connect(self._change_password)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Старый пароль", self.old_password)
        form.addRow("Новый пароль", self.new_password)
        form.addRow("Повтор нового пароля", self.repeat_password)

        policy = QLabel("Пароль должен содержать верхний и нижний регистр, цифру и разрешенный спецсимвол.")
        policy.setProperty("role", "subtitle")
        policy.setWordWrap(True)

        self.save_button = QPushButton("Сменить пароль")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._change_password)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(self.status)
        layout.addLayout(form)
        layout.addWidget(policy)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def _change_password(self) -> None:
        old_password = self.old_password.text()
        new_password = self.new_password.text()
        repeat_password = self.repeat_password.text()

        if not old_password or not new_password or not repeat_password:
            QMessageBox.warning(self, "Проверка", "Заполните все поля.")
            return
        if new_password != repeat_password:
            QMessageBox.warning(self, "Проверка", "Новый пароль и повтор не совпадают.")
            return
        if old_password == new_password:
            QMessageBox.warning(self, "Проверка", "Новый пароль должен отличаться от старого.")
            return

        try:
            self.api.change_password(old_password, new_password)
            QMessageBox.information(self, "Смена пароля", "Пароль успешно изменен.")
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка смены пароля", str(exc))

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.forced and self.result() != self.DialogCode.Accepted:
            event.ignore()
            QMessageBox.warning(
                self,
                "Смена пароля обязательна",
                "Для продолжения работы необходимо сменить первичный пароль.",
            )
        else:
            super().closeEvent(event)


__all__ = ["ChangePasswordWindow"]
