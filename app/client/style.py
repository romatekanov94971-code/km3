from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QHeaderView, QTableWidget


APP_STYLESHEET = """
QWidget {
    font-family: "Segoe UI", "Arial";
    font-size: 10.5pt;
    color: #0f172a;
}
QMainWindow, QDialog {
    background: #f8fafc;
    color: #0f172a;
}
QStatusBar {
    background: #ffffff;
    color: #0f172a;
    border-top: 1px solid #dbe4ef;
}
QMenuBar {
    background: #ffffff;
    color: #0f172a;
    border-bottom: 1px solid #dbe4ef;
    padding: 3px;
}
QMenuBar::item {
    color: #0f172a;
}
QMenuBar::item:selected {
    background: #e0f2fe;
    border-radius: 4px;
}
QMenu {
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    padding: 4px;
}
QMenu::item {
    color: #0f172a;
}
QMenu::item:selected {
    background: #dbeafe;
    color: #0f172a;
}
QLabel {
    color: #0f172a;
}
QLabel[role="title"] {
    color: #0f172a;
    font-size: 18pt;
    font-weight: 700;
}
QLabel[role="subtitle"] {
    color: #475569;
    font-size: 10.5pt;
}
QLabel[role="section"] {
    color: #1e3a8a;
    font-size: 12pt;
    font-weight: 700;
    padding-top: 6px;
}
QGroupBox {
    background: #ffffff;
    border: 1px solid #dbe4ef;
    border-radius: 10px;
    margin-top: 14px;
    padding: 12px;
    font-weight: 700;
    color: #1e3a8a;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background: #f8fafc;
    color: #1e3a8a;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit {
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 6px;
    selection-background-color: #bfdbfe;
    selection-color: #0f172a;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #2563eb;
    color: #0f172a;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #0f172a;
    selection-background-color: #dbeafe;
    selection-color: #0f172a;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 13px;
    font-weight: 600;
    color: #0f172a;
}
QPushButton:hover {
    background: #eff6ff;
    border-color: #93c5fd;
}
QPushButton:pressed {
    background: #dbeafe;
}
QPushButton#primaryButton {
    background: #2563eb;
    border-color: #2563eb;
    color: white;
}
QPushButton#primaryButton:hover {
    background: #1d4ed8;
}
QPushButton#successButton {
    background: #16a34a;
    border-color: #16a34a;
    color: white;
}
QPushButton#successButton:hover {
    background: #15803d;
}
QPushButton#warningButton {
    background: #f97316;
    border-color: #f97316;
    color: white;
}
QPushButton#warningButton:hover {
    background: #ea580c;
}
QPushButton#dangerButton {
    background: #dc2626;
    border-color: #dc2626;
    color: white;
}
QPushButton#dangerButton:hover {
    background: #b91c1c;
}
QTableWidget {
    background: #ffffff;
    color: #0f172a;
    alternate-background-color: #f8fafc;
    border: 1px solid #dbe4ef;
    border-radius: 8px;
    gridline-color: #e2e8f0;
    selection-background-color: #dbeafe;
    selection-color: #0f172a;
}
QTableWidget::item {
    color: #0f172a;
}
QHeaderView::section {
    background: #eaf2ff;
    color: #0f172a;
    border: 0;
    border-right: 1px solid #dbe4ef;
    border-bottom: 1px solid #dbe4ef;
    padding: 7px;
    font-weight: 700;
}
QTabWidget::pane {
    border: 1px solid #dbe4ef;
    border-radius: 8px;
    background: #ffffff;
}
QTabBar::tab {
    background: #e2e8f0;
    color: #334155;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 14px;
    margin-right: 3px;
}
QTabBar::tab:selected {
    background: #2563eb;
    color: white;
}
QScrollArea {
    background: #f8fafc;
    color: #0f172a;
    border: none;
}
QSplitter::handle {
    background: #e2e8f0;
}
"""


def apply_app_style(app: QApplication) -> None:
    """Применяет единый визуальный стиль ко всему PyQt-приложению."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f8fafc"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f8fafc"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#dbeafe"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#0f172a"))
    app.setPalette(palette)
    app.setStyleSheet(APP_STYLESHEET)


def polish_table(table: QTableWidget) -> None:
    """Общие настройки таблиц GUI."""
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)


__all__ = ["APP_STYLESHEET", "apply_app_style", "polish_table"]
