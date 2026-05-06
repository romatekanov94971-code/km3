from __future__ import annotations

import json

from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

from app.client.api_client import ApiClient


class SecuritySettingsWindow(QDialog):
    """Административный просмотр текущих параметров политики безопасности."""

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.setWindowTitle("Политика безопасности и аутентификации")
        self.resize(760, 560)

        title = QLabel("Политика безопасности")
        title.setProperty("role", "title")
        subtitle = QLabel("Текущие параметры аутентификации, аудита и ограничений API.")
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.load_policy)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.text)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

        self.load_policy()

    def load_policy(self) -> None:
        try:
            policy = self.api.get_auth_policy()
            self.text.setPlainText(
                "Текущая политика аутентификации:\n"
                + json.dumps(policy, ensure_ascii=False, indent=2)
                + "\n\nНастройка выполняется через переменные окружения:\n"
                + "ENERGY_AUTH_MAX_FAILED_ATTEMPTS\n"
                + "ENERGY_AUTH_LOCK_MINUTES\n"
                + "ENERGY_AUTH_USER_MIN_PASSWORD_LENGTH\n"
                + "ENERGY_AUTH_ADMIN_MIN_PASSWORD_LENGTH\n"
                + "ENERGY_AUDIT_DETAIL_LEVEL\n"
                + "ENERGY_AUDIT_RETENTION_DAYS\n"
                + "ENERGY_AUDIT_REMOTE_URL\n"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))


__all__ = ["SecuritySettingsWindow"]
