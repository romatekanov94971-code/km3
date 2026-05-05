from __future__ import annotations

import json

from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from app.client.api_client import ApiClient


class AuditWindow(QDialog):
    """Административное окно просмотра журнала аудита."""

    HEADERS = ["Дата/время", "Событие", "Компонент", "Субъект", "Тип", "ID события"]

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.events: list[dict] = []
        self.setWindowTitle("Журнал аудита")
        self.resize(980, 620)

        self.limit = QSpinBox()
        self.limit.setRange(1, 1000)
        self.limit.setValue(100)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_events)

        self.cleanup_button = QPushButton("Очистить старые")
        self.cleanup_button.clicked.connect(self.cleanup_old_events)

        top = QHBoxLayout()
        top.addWidget(QLabel("Количество записей:"))
        top.addWidget(self.limit)
        top.addWidget(self.refresh_button)
        top.addWidget(self.cleanup_button)
        top.addStretch()

        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.itemSelectionChanged.connect(self.show_selected_details)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Выберите событие, чтобы посмотреть служебные заголовки и детали.")

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.table, stretch=3)
        layout.addWidget(QLabel("Детали события"))
        layout.addWidget(self.details, stretch=2)
        self.setLayout(layout)

        self.load_events()

    def load_events(self) -> None:
        try:
            self.events = self.api.get_audit_events(self.limit.value())
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка аудита", str(exc))
            return

        self.table.setRowCount(len(self.events))
        for row, event in enumerate(self.events):
            values = [
                event.get("event_time", ""),
                event.get("event_name", ""),
                event.get("component", ""),
                event.get("subject") or "",
                event.get("event_type", ""),
                event.get("event_id", ""),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
        self.details.clear()

    def show_selected_details(self) -> None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return
        row = indexes[0].row()
        if row >= len(self.events):
            return
        event = self.events[row]
        details = {
            "headers": event.get("headers", {}),
            "details": event.get("details", {}),
        }
        self.details.setPlainText(json.dumps(details, ensure_ascii=False, indent=2))

    def cleanup_old_events(self) -> None:
        try:
            result = self.api.cleanup_audit()
            QMessageBox.information(
                self,
                "Очистка аудита",
                f"Удалено старых событий: {result.get('deleted', 0)}",
            )
            self.load_events()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка очистки аудита", str(exc))
