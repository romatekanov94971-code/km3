from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartsWindow(QDialog):
    """Графики с явным аудитом расчетных точек.

    Важно: это не отдельный красивый график "из головы". Все точки берутся из
    JSON-результата расчетного ядра. У каждой точки есть calculation_trace:
    входные параметры, формула, подстановка, коэффициенты и итог.
    """

    def __init__(self, result: dict) -> None:
        super().__init__()
        self.result = result
        self.setWindowTitle("Графики + аудит расчета точек")
        self.resize(1220, 820)

        banner = QLabel(
            "АУДИТ ГРАФИКОВ ВКЛЮЧЕН: выбери точку в таблице — справа будет показано, "
            "из каких входных данных, формул и коэффициентов она рассчитана."
        )
        banner.setStyleSheet(
            "font-weight: bold; padding: 8px; border: 2px solid #2563eb; "
            "background: #eff6ff; color: #1e3a8a;"
        )
        banner.setWordWrap(True)

        tabs = QTabWidget()
        tabs.addTab(self._audit_overview_tab(result), "Аудит графиков")
        tabs.addTab(self._temperature_tab(result), "Температура")
        tabs.addTab(self._load_distribution_tab(result), "Блоки")
        tabs.addTab(self._vacuum_tab(result), "Конденсатор")

        layout = QVBoxLayout()
        layout.addWidget(banner)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def _format_trace(self, point: dict[str, Any]) -> str:
        trace = point.get("calculation_trace") or {}
        if not trace:
            return "Для этой точки расчетный след отсутствует. Значит результат получен из старой версии API/кода."

        formula = trace.get("formula", {})
        substitution = trace.get("substitution", {})
        factors = trace.get("calculated_factors", {})
        input_data = trace.get("input", {})
        result = trace.get("main_result", {})

        return "\n".join(
            [
                "КАК ПОСЧИТАНА ВЫБРАННАЯ ТОЧКА",
                "==============================",
                trace.get("note", ""),
                "",
                "1. Исходные данные точки:",
                json.dumps(input_data, ensure_ascii=False, indent=2),
                "",
                "2. Примененный режим:",
                str(trace.get("applied_operation_mode", "")),
                "",
                "3. Формулы:",
                json.dumps(formula, ensure_ascii=False, indent=2),
                "",
                "4. Подстановка чисел:",
                json.dumps(substitution, ensure_ascii=False, indent=2),
                "",
                "5. Расчетные коэффициенты:",
                json.dumps(factors, ensure_ascii=False, indent=2),
                "",
                "6. Итоговые значения расчетного ядра:",
                json.dumps(result, ensure_ascii=False, indent=2),
                "",
                "7. Полный JSON расчетного следа:",
                json.dumps(trace, ensure_ascii=False, indent=2),
            ]
        )

    def _copy_text(self, text_widget: QTextEdit) -> None:
        QApplication.clipboard().setText(text_widget.toPlainText())

    def _all_points_with_labels(self, result: dict) -> list[tuple[str, dict[str, Any]]]:
        rows: list[tuple[str, dict[str, Any]]] = []
        for point in result.get("temperature_analysis", []):
            rows.append((f"Температура: T={point.get('temp_c')} °C", point))
        for point in result.get("load_distribution", []):
            rows.append((f"Блоки: {point.get('blocks')} шт.", point))
        for point in result.get("condenser_vacuum_optimization", {}).get("points", []):
            rows.append((f"Конденсатор: {point.get('vacuum_kpa')} кПа", point))
        return rows

    def _audit_overview_figure(self, result: dict) -> Figure:
        """Сводный график для вкладки аудита.

        Он нужен именно как визуальное подтверждение: таблица аудита ниже
        соответствует реальным точкам, по которым построены графики.
        """
        figure = Figure(figsize=(7, 4.5))
        ax = figure.add_subplot(111)

        temp_points = result.get("temperature_analysis", [])
        if temp_points:
            ax.plot(
                [p["temp_c"] for p in temp_points],
                [p["heat_removal_factor"] for p in temp_points],
                marker="o",
                label="Температура → теплоотвод",
            )

        load_points = result.get("load_distribution", [])
        if load_points:
            ax.plot(
                [p["blocks"] for p in load_points],
                [p["efficiency_netto_percent"] for p in load_points],
                marker="s",
                linestyle="--",
                label="Блоки → КПД нетто, %",
            )

        vacuum_points = result.get("condenser_vacuum_optimization", {}).get("points", [])
        if vacuum_points:
            ax.plot(
                [p["vacuum_kpa"] for p in vacuum_points],
                [p["efficiency_netto_percent"] for p in vacuum_points],
                marker="^",
                linestyle=":",
                label="Конденсатор → КПД нетто, %",
            )

        ax.set_title("Сводный график расчетных точек")
        ax.set_xlabel("X соответствующего анализа: °C / блоки / кПа")
        ax.set_ylabel("Расчетное значение")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        return figure

    def _audit_overview_tab(self, result: dict) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()

        intro = QLabel(
            "Эта вкладка специально показывает, что графики построены на реальных расчетных точках. "
            "Выбери любую строку — появится полный расчет: входные данные → формула → подстановка → результат."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("padding: 6px; background: #f8fafc; border: 1px solid #cbd5e1;")
        layout.addWidget(intro)

        splitter = QSplitter()

        points = self._all_points_with_labels(result)
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["График/точка", "X", "Y", "Есть trace"])
        table.setRowCount(len(points))
        for row, (label, point) in enumerate(points):
            trace = point.get("calculation_trace") or {}
            x_axis = trace.get("x_axis", {})
            y_axis = trace.get("y_axis", {})
            values = [
                label,
                f"{x_axis.get('value', '')} {x_axis.get('unit', '')}",
                f"{y_axis.get('value', '')} {y_axis.get('unit', '')}",
                "ДА" if trace else "НЕТ",
            ]
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(str(value)))
        table.resizeColumnsToContents()

        left = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Сводный график расчетных точек"))
        left_layout.addWidget(FigureCanvas(self._audit_overview_figure(result)), stretch=3)
        left_layout.addWidget(QLabel("Точки, из которых построены графики"))
        left_layout.addWidget(table, stretch=2)
        left.setLayout(left_layout)

        details = QTextEdit()
        details.setReadOnly(True)
        details.setPlaceholderText("Выбери расчетную точку слева.")

        copy_button = QPushButton("Скопировать расчет выбранной точки")
        copy_button.clicked.connect(lambda: self._copy_text(details))

        right = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Расчет выбранной точки"))
        right_layout.addWidget(details)
        right_layout.addWidget(copy_button)
        right.setLayout(right_layout)

        def show_details() -> None:
            indexes = table.selectionModel().selectedRows()
            if not indexes:
                return
            row = indexes[0].row()
            if 0 <= row < len(points):
                details.setPlainText(self._format_trace(points[row][1]))

        table.itemSelectionChanged.connect(show_details)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([650, 560])

        layout.addWidget(splitter)
        widget.setLayout(layout)

        if points:
            table.selectRow(0)
        return widget

    def _build_analysis_tab(
        self,
        figure: Figure,
        points: list[dict[str, Any]],
        headers: list[str],
        row_factory: Callable[[dict[str, Any]], list[Any]],
    ) -> QWidget:
        widget = QWidget()
        root = QVBoxLayout()

        root.addWidget(
            QLabel(
                "График построен из расчетных точек ниже. Таблица справа — это данные графика. "
                "Выбери строку, чтобы увидеть формулу и подстановку."
            )
        )

        splitter = QSplitter()
        left = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(FigureCanvas(figure))
        left.setLayout(left_layout)

        right = QWidget()
        right_layout = QVBoxLayout()
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(points))
        for row, point in enumerate(points):
            for col, value in enumerate(row_factory(point)):
                table.setItem(row, col, QTableWidgetItem(str(value)))
        table.resizeColumnsToContents()

        details = QTextEdit()
        details.setReadOnly(True)
        details.setPlaceholderText("Выбери точку графика в таблице справа.")

        copy_button = QPushButton("Скопировать расчет точки")
        copy_button.clicked.connect(lambda: self._copy_text(details))

        def show_details() -> None:
            indexes = table.selectionModel().selectedRows()
            if not indexes:
                return
            row = indexes[0].row()
            if 0 <= row < len(points):
                details.setPlainText(self._format_trace(points[row]))

        table.itemSelectionChanged.connect(show_details)

        right_layout.addWidget(QLabel("Точки графика"))
        right_layout.addWidget(table, stretch=2)
        right_layout.addWidget(QLabel("Расчетный след выбранной точки"))
        right_layout.addWidget(details, stretch=3)
        right_layout.addWidget(copy_button)
        right.setLayout(right_layout)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([680, 520])

        root.addWidget(splitter)
        widget.setLayout(root)

        if points:
            table.selectRow(0)
        return widget

    def _temperature_tab(self, result: dict) -> QWidget:
        points = result.get("temperature_analysis", [])
        temps = [p["temp_c"] for p in points]
        heat = [p["heat_removal_factor"] for p in points]
        eff = [p["efficiency_netto_percent"] for p in points]

        figure = Figure(figsize=(8, 5))
        ax = figure.add_subplot(111)
        line1 = ax.plot(temps, heat, marker="o", label="Теплоотводящая способность")
        ax.set_xlabel("Температура наружного воздуха, °C")
        ax.set_ylabel("Теплоотводящая способность, отн. ед.")
        ax.grid(True, alpha=0.3)
        ax2 = ax.twinx()
        line2 = ax2.plot(temps, eff, marker="s", linestyle="--", label="КПД нетто")
        ax2.set_ylabel("КПД нетто, %")
        ax.set_title("Влияние температуры на теплоотвод и КПД")
        lines = line1 + line2
        labels = [line.get_label() for line in lines]
        ax.legend(lines, labels, loc="best")
        return self._build_analysis_tab(
            figure,
            points,
            ["T, °C", "Теплоотвод", "КПД нетто, %", "Расход"],
            lambda p: [
                p.get("temp_c", ""),
                f"{p.get('heat_removal_factor', 0):.6f}",
                f"{p.get('efficiency_netto_percent', 0):.3f}",
                f"{p.get('fuel_consumption', 0):.3f}",
            ],
        )

    def _load_distribution_tab(self, result: dict) -> QWidget:
        points = result.get("load_distribution", [])
        blocks = [p["blocks"] for p in points]
        efficiency = [p["efficiency_netto_percent"] for p in points]
        fuel = [p["fuel_consumption"] for p in points]

        figure = Figure(figsize=(8, 5))
        ax = figure.add_subplot(111)
        line1 = ax.plot(blocks, efficiency, marker="o", label="КПД нетто")
        ax.set_xlabel("Количество работающих блоков")
        ax.set_ylabel("КПД нетто, %")
        ax.grid(True, alpha=0.3)
        ax2 = ax.twinx()
        line2 = ax2.plot(blocks, fuel, marker="s", linestyle="--", label="Расход топлива")
        ax2.set_ylabel("Удельный расход топлива")
        ax.set_title("Оптимальное распределение нагрузки по блокам")
        lines = line1 + line2
        labels = [line.get_label() for line in lines]
        ax.legend(lines, labels, loc="best")
        return self._build_analysis_tab(
            figure,
            points,
            ["Блоков", "Нагрузка/блок", "Загрузка, %", "КПД нетто, %", "Расход"],
            lambda p: [
                p.get("blocks", ""),
                f"{p.get('load_per_block', 0):.3f}",
                f"{p.get('load_percent', 0):.3f}",
                f"{p.get('efficiency_netto_percent', 0):.3f}",
                f"{p.get('fuel_consumption', 0):.3f}",
            ],
        )

    def _vacuum_tab(self, result: dict) -> QWidget:
        optimization = result.get("condenser_vacuum_optimization", {})
        points = optimization.get("points", [])
        vacuum = [p["vacuum_kpa"] for p in points]
        efficiency = [p["efficiency_netto_percent"] for p in points]

        figure = Figure(figsize=(8, 5))
        ax = figure.add_subplot(111)
        ax.plot(vacuum, efficiency, marker="o", label="КПД нетто")
        best = optimization.get("best_vacuum_kpa")
        if best is not None:
            ax.axvline(best, linestyle="--", label=f"Оптимум: {best:.1f} кПа")
        ax.legend(loc="best")
        ax.set_xlabel("Разрежение в конденсаторе, кПа")
        ax.set_ylabel("КПД нетто, %")
        ax.set_title("Оптимизация разрежения в конденсаторе")
        ax.grid(True, alpha=0.3)
        return self._build_analysis_tab(
            figure,
            points,
            ["Вакуум, кПа", "Коэф.", "КПД блока, %", "КПД нетто, %", "Расход"],
            lambda p: [
                f"{p.get('vacuum_kpa', 0):.1f}",
                f"{p.get('condenser_vacuum_factor', 0):.6f}",
                f"{p.get('block_efficiency_percent', 0):.3f}",
                f"{p.get('efficiency_netto_percent', 0):.3f}",
                f"{p.get('fuel_consumption', 0):.3f}",
            ],
        )


__all__ = ["ChartsWindow"]
