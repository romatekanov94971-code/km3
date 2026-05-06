from __future__ import annotations

import json

from PyQt6.QtWidgets import (
    QAbstractItemView,
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
from app.client.style import polish_table


class HistoryWindow(QDialog):
    """Окно просмотра истории расчетов текущего пользователя."""

    HEADERS = ["Дата/время", "Режим", "Нагрузка ТЭС", "Блоков", "КПД нетто", "Удельный расход"]

    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.records: list[dict] = []
        self.setWindowTitle("История расчетов")
        self.resize(1040, 680)

        self.limit = QSpinBox()
        self.limit.setRange(1, 500)
        self.limit.setValue(50)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.load_history)

        top = QHBoxLayout()
        top.addWidget(QLabel("Количество записей:"))
        top.addWidget(self.limit)
        top.addWidget(self.refresh_button)
        top.addStretch()

        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.show_selected_details)
        polish_table(self.table)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Выберите расчет, чтобы посмотреть входные параметры и полный результат.")

        layout = QVBoxLayout()
        title = QLabel("История расчетов")
        title.setProperty("role", "title")
        subtitle = QLabel("Выберите запись, чтобы увидеть входные параметры, результат и расчетный JSON.")
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(top)
        layout.addWidget(self.table, stretch=3)
        layout.addWidget(QLabel("Детали расчета"))
        layout.addWidget(self.details, stretch=2)
        self.setLayout(layout)

        self.load_history()

    def load_history(self) -> None:
        try:
            self.records = self.api.get_history(self.limit.value())
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка истории", str(exc))
            return

        self.table.setRowCount(len(self.records))
        for row, record in enumerate(self.records):
            input_data = record.get("input", {})
            result_data = record.get("result", {})
            main = result_data.get("main_result", {})
            values = [
                record.get("created_at", ""),
                main.get("operation_mode") or input_data.get("operation_mode", ""),
                input_data.get("total_load", ""),
                input_data.get("num_blocks", ""),
                f"{main.get('efficiency_netto', 0) * 100:.2f}%" if main else "",
                f"{main.get('fuel_consumption', 0):.2f}" if main else "",
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
        self.details.clear()
        if self.records:
            self.table.selectRow(0)

    def show_selected_details(self) -> None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return
        row = indexes[0].row()
        if row >= len(self.records):
            return
        record = self.records[row]
        self.details.setPlainText(json.dumps(record, ensure_ascii=False, indent=2))


__all__ = ["HistoryWindow"]
