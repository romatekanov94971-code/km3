from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartsWindow(QDialog):
    def __init__(self, result: dict) -> None:
        super().__init__()
        self.setWindowTitle("Графики")
        self.resize(820, 600)

        points = result.get("temperature_analysis", [])
        temps = [p["temp_c"] for p in points]
        heat = [p["heat_removal_factor"] for p in points]

        figure = Figure(figsize=(7, 5))
        ax = figure.add_subplot(111)
        ax.plot(temps, heat, marker="o")
        ax.set_xlabel("Температура наружного воздуха, °C")
        ax.set_ylabel("Теплоотводящая способность, отн. ед.")
        ax.set_title("Зависимость теплоотводящей способности от температуры")
        ax.grid(True, alpha=0.3)

        layout = QVBoxLayout()
        layout.addWidget(FigureCanvas(figure))
        self.setLayout(layout)
