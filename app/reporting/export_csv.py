from __future__ import annotations

import csv
from pathlib import Path

from app.common.schemas import FullCalculationResult
from app.common.utils import utcnow


def export_full_result_to_csv(result: FullCalculationResult, directory: str | Path = "exports") -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"calculation_{utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Раздел", "Показатель", "Значение"])
        main = result.main_result
        writer.writerow(["Основной расчет", "Нагрузка на энергоблок, МВт", round(main.load_per_block, 3)])
        writer.writerow(["Основной расчет", "КПД блока, %", round(main.block_efficiency * 100, 3)])
        writer.writerow(["Основной расчет", "КПД ТЭС брутто, %", round(main.efficiency_brutto * 100, 3)])
        writer.writerow(["Основной расчет", "Собственные нужды, МВт", round(main.own_needs_power, 3)])
        writer.writerow(["Основной расчет", "Собственные нужды, %", round(main.own_needs_percent, 3)])
        writer.writerow(["Основной расчет", "КПД ТЭС нетто, %", round(main.efficiency_netto * 100, 3)])
        writer.writerow(["Основной расчет", "Удельный расход топлива, г у.т./кВт·ч", round(main.fuel_consumption, 3)])
        writer.writerow([])
        writer.writerow(["Температурный анализ", "Температура, °C", "КПД нетто, %", "Расход топлива", "Теплоотвод"])
        for p in result.temperature_analysis:
            writer.writerow(["Температурный анализ", p.temp_c, round(p.efficiency_netto_percent, 3), round(p.fuel_consumption, 3), round(p.heat_removal_factor, 5)])
    return path
