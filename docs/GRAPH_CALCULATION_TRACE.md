# Расчётный след графиков

Графики строятся по реальным расчётным точкам.

Каждая точка содержит поле `calculation_trace`.

## Где хранится trace

```text
temperature_analysis[*].calculation_trace
load_distribution[*].calculation_trace
condenser_vacuum_optimization.points[*].calculation_trace
```

## Что содержит trace

- `input` — исходные параметры точки;
- `applied_operation_mode` — применённый режим;
- `formula` — формулы;
- `substitution` — подстановка чисел;
- `calculated_factors` — поправочные коэффициенты;
- `main_result` — итоговые значения.

## Как это выглядит в GUI

Откройте:

```text
Графики + аудит расчета → Аудит графиков
```

На вкладке есть:

- сводный график;
- таблица точек;
- подробное объяснение выбранной точки;
- кнопка копирования расчёта точки.
