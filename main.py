from __future__ import annotations

import argparse
import sys
from pprint import pprint

from app.calculation.orchestrator import run_full_calculation
from app.common.schemas import CalculationInput


def run_cli_demo() -> None:
    data = CalculationInput(
        total_load=400,
        num_blocks=2,
        nominal_power_per_block=300,
        nominal_efficiency=0.38,
        temp_c=32,
        humidity=80,
        wind_speed=5,
        wind_dir=30,
    )
    result = run_full_calculation(data).to_dict()
    pprint(result["main_result"])
    print("Оптимальные блоки:")
    pprint(result["optimal_blocks"])
    print("Оптимальное разрежение:")
    pprint({k: v for k, v in result["condenser_vacuum_optimization"].items() if k != "points"})


def run_api() -> None:
    import uvicorn

    from app.server.api import app
    from app.server.config import get_settings

    settings = get_settings()
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)


def run_gui() -> None:
    from PyQt6.QtWidgets import QApplication

    from app.client.api_client import ApiClient
    from app.client.login_window import LoginWindow
    from app.client.main_window import MainWindow

    app = QApplication(sys.argv)
    api = ApiClient()
    login = LoginWindow(api)
    if login.exec() == login.DialogCode.Accepted:
        window = MainWindow(api)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Energy System")
    parser.add_argument("mode", nargs="?", choices=["demo", "api", "gui"], default="demo")
    args = parser.parse_args()
    if args.mode == "api":
        run_api()
    elif args.mode == "gui":
        run_gui()
    else:
        run_cli_demo()
