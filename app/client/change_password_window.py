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
    """Окно смены пароля пользователя.

    Используется и при первичной аутентификации, и из меню главного окна.
    """

    def __init__(self, api: ApiClient, old_password_hint: str = "", forced: bool = False) -> None:
        super().__init__()
        self.api = api
        self.forced = forced
        self.setWindowTitle("Смена пароля")
        self.setMinimumWidth(420)

        hint_text = (
            "Необходимо сменить пароль после первичной аутентификации."
            if forced
            else "Введите старый пароль и новый пароль."
        )
        self.status = QLabel(hint_text)

        self.old_password = QLineEdit(old_password_hint)
        self.old_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.repeat_password = QLineEdit()
        self.repeat_password.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("Старый пароль", self.old_password)
        form.addRow("Новый пароль", self.new_password)
        form.addRow("Повтор нового пароля", self.repeat_password)

        self.save_button = QPushButton("Сменить пароль")
        self.save_button.clicked.connect(self._change_password)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addLayout(form)
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
