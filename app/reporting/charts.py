from __future__ import annotations

from pathlib import Path

from app.common.schemas import FullCalculationResult, TemperatureAnalysisPoint


def save_temperature_chart(points: list[TemperatureAnalysisPoint], output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temps = [p.temp_c for p in points]
    heat = [p.heat_removal_factor for p in points]
    plt.figure(figsize=(8, 5))
    plt.plot(temps, heat, marker="o")
    plt.xlabel("Температура наружного воздуха, °C")
    plt.ylabel("Теплоотводящая способность, отн. ед.")
    plt.title("Зависимость теплоотводящей способности от температуры")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()
    return output


def save_efficiency_chart(result: FullCalculationResult, output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temps = [p.temp_c for p in result.temperature_analysis]
    eff = [p.efficiency_netto_percent for p in result.temperature_analysis]
    plt.figure(figsize=(8, 5))
    plt.plot(temps, eff, marker="o")
    plt.xlabel("Температура наружного воздуха, °C")
    plt.ylabel("КПД ТЭС нетто, %")
    plt.title("Зависимость КПД нетто от температуры")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()
    return output
