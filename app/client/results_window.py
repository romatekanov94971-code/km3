from __future__ import annotations

import json

from PyQt6.QtWidgets import QDialog, QLabel, QTabWidget, QTextEdit, QVBoxLayout, QWidget


class ResultsWindow(QDialog):
    def __init__(self, result: dict) -> None:
        super().__init__()
        self.result = result
        self.setWindowTitle("Результаты расчета")
        self.resize(860, 680)

        main = result["main_result"]
        title = QLabel("Результаты расчета")
        title.setProperty("role", "title")
        subtitle = QLabel(
            f"Режим: {main.get('operation_mode', 'auto')} • "
            f"КПД нетто: {main['efficiency_netto'] * 100:.2f}% • "
            f"Удельный расход: {main['fuel_consumption']:.2f} г у.т./кВт·ч"
        )
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)

        tabs = QTabWidget()
        tabs.addTab(self._text_tab(self._summary_text()), "Итоги")
        tabs.addTab(self._text_tab(self._factors_text()), "Коэффициенты")
        tabs.addTab(self._text_tab(self._optimization_text()), "Оптимизация")
        tabs.addTab(self._text_tab(json.dumps(result, ensure_ascii=False, indent=2)), "JSON")

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def _text_tab(self, text: str) -> QWidget:
        widget = QWidget()
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setText(text)
        layout = QVBoxLayout()
        layout.addWidget(editor)
        widget.setLayout(layout)
        return widget

    def _summary_text(self) -> str:
        main = self.result["main_result"]
        text = (
            "ОСНОВНЫЕ РЕЗУЛЬТАТЫ\n"
            "===================\n"
            f"Примененный режим работы: {main.get('operation_mode', 'auto')}\n"
            f"Нагрузка на энергоблок: {main['load_per_block']:.2f} МВт\n"
            f"КПД блока: {main['block_efficiency'] * 100:.2f}%\n"
            f"КПД ТЭС брутто: {main['efficiency_brutto'] * 100:.2f}%\n"
            f"Собственные нужды: {main['own_needs_power']:.2f} МВт ({main['own_needs_percent']:.2f}%)\n"
            f"КПД ТЭС нетто: {main['efficiency_netto'] * 100:.2f}%\n"
            f"Удельный расход топлива: {main['fuel_consumption']:.2f} г у.т./кВт·ч\n"
            f"Мощность брутто: {main['total_power_brutto']:.2f} МВт\n"
            f"Мощность нетто: {main['total_power_netto']:.2f} МВт\n"
        )
        if main.get("warning"):
            text += f"\nПРЕДУПРЕЖДЕНИЕ\n=============\n{main['warning']}\n"
        return text

    def _factors_text(self) -> str:
        main = self.result["main_result"]
        return (
            "ПОПРАВОЧНЫЕ КОЭФФИЦИЕНТЫ\n"
            "========================\n"
            f"Температура: {main.get('temperature_factor', 1):.4f}\n"
            f"Влажность: {main.get('humidity_factor', 1):.4f}\n"
            f"Скорость ветра: {main.get('wind_speed_factor', 1):.4f}\n"
            f"Направление ветра: {main.get('wind_direction_factor', 1):.4f}\n"
            f"Сезонный режим: {main.get('seasonal_factor', 1):.4f}\n"
            f"Разрежение в конденсаторе: {main.get('condenser_vacuum_factor', 1):.4f}\n"
            f"Итоговый внешний фактор: {main.get('external_factor', 1):.4f}\n"
        )

    def _optimization_text(self) -> str:
        optimal_blocks = self.result.get("optimal_blocks", {})
        vacuum = self.result.get("condenser_vacuum_optimization", {})
        return (
            "ОПТИМИЗАЦИЯ\n"
            "===========\n"
            f"Оптимальное количество блоков: {optimal_blocks.get('blocks', '-')}\n"
            f"Нагрузка оптимального блока: {optimal_blocks.get('load_per_block', 0):.2f} МВт\n"
            f"Оптимальное разрежение: {vacuum.get('best_vacuum_kpa', 0):.1f} кПа\n"
            f"КПД при оптимальном разрежении: {vacuum.get('best_efficiency_netto_percent', 0):.2f}%\n"
        )


__all__ = ["ResultsWindow"]
