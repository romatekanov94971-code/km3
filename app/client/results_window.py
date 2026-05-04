from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QTextEdit, QVBoxLayout


class ResultsWindow(QDialog):
    def __init__(self, result: dict) -> None:
        super().__init__()
        self.setWindowTitle("Результаты расчета")
        self.resize(720, 520)
        main = result["main_result"]
        text = (
            f"Нагрузка на энергоблок: {main['load_per_block']:.2f} МВт\n"
            f"КПД блока: {main['block_efficiency'] * 100:.2f}%\n"
            f"КПД ТЭС брутто: {main['efficiency_brutto'] * 100:.2f}%\n"
            f"Собственные нужды: {main['own_needs_power']:.2f} МВт ({main['own_needs_percent']:.2f}%)\n"
            f"КПД ТЭС нетто: {main['efficiency_netto'] * 100:.2f}%\n"
            f"Удельный расход топлива: {main['fuel_consumption']:.2f} г у.т./кВт·ч\n\n"
            f"Оптимальное количество блоков: {result['optimal_blocks']['blocks']}\n"
            f"Оптимальное разрежение: {result['condenser_vacuum_optimization']['best_vacuum_kpa']:.1f} кПа\n"
        )
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setText(text)
        layout = QVBoxLayout()
        layout.addWidget(editor)
        self.setLayout(layout)
