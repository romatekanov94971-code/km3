from __future__ import annotations

from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QWidget,
)

from app.client.api_client import ApiClient
from app.client.audit_window import AuditWindow
from app.client.charts_window import ChartsWindow
from app.client.change_password_window import ChangePasswordWindow
from app.client.change_role_window import ChangeRoleWindow
from app.client.create_user_window import CreateUserWindow
from app.client.results_window import ResultsWindow
from app.client.security_settings_window import SecuritySettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api
        self.last_result: dict | None = None
        self._logout_sent = False
        role_label = "Администратор" if self.api.is_admin else "Пользователь"
        self.setWindowTitle(f"Эффективность энергооборудования ТЭС — {role_label}: {self.api.username}")
        self.resize(760, 460)
        self._setup_menu()

        self.total_load = self._double(400, 1, 10000)
        self.num_blocks = QSpinBox()
        self.num_blocks.setRange(1, 20)
        self.num_blocks.setValue(2)
        self.nominal_power = self._double(300, 1, 2000)
        self.nominal_efficiency = self._double(0.38, 0.01, 0.99, decimals=4, step=0.01)
        self.temp_c = self._double(25, -60, 60)
        self.humidity = self._double(60, 0, 100)
        self.wind_speed = self._double(3, 0, 80)
        self.wind_dir = self._double(90, 0, 360)
        self.own_needs = self._double(0.05, 0, 0.49, decimals=4, step=0.01)
        self.beta = self._double(0.4, 0, 2, decimals=3, step=0.05)

        form = QFormLayout()
        form.addRow("Общая нагрузка ТЭС, МВт", self.total_load)
        form.addRow("Количество работающих блоков", self.num_blocks)
        form.addRow("Номинальная мощность блока, МВт", self.nominal_power)
        form.addRow("Номинальный КПД блока", self.nominal_efficiency)
        form.addRow("Температура наружного воздуха, °C", self.temp_c)
        form.addRow("Влажность, %", self.humidity)
        form.addRow("Скорость ветра, м/с", self.wind_speed)
        form.addRow("Направление ветра, градусы", self.wind_dir)
        form.addRow("Коэффициент собственных нужд", self.own_needs)
        form.addRow("Коэффициент beta", self.beta)

        run_button = QPushButton("Рассчитать")
        run_button.clicked.connect(self.run_calculation)
        charts_button = QPushButton("График")
        charts_button.clicked.connect(self.show_charts)
        csv_button = QPushButton("Экспорт CSV")
        csv_button.clicked.connect(self.export_csv)
        pptx_button = QPushButton("Экспорт PPTX")
        pptx_button.clicked.connect(self.export_pptx)

        buttons = QHBoxLayout()
        buttons.addWidget(run_button)
        buttons.addWidget(charts_button)
        buttons.addWidget(csv_button)
        buttons.addWidget(pptx_button)

        root = QWidget()
        layout = QFormLayout()
        layout.addRow(form)
        layout.addRow(buttons)
        root.setLayout(layout)
        self.setCentralWidget(root)

    def _setup_menu(self) -> None:
        account_menu = self.menuBar().addMenu("Аккаунт")

        change_password_action = QAction("Сменить пароль", self)
        change_password_action.triggered.connect(self.change_password)
        account_menu.addAction(change_password_action)

        logout_action = QAction("Выйти", self)
        logout_action.triggered.connect(self._do_logout_and_close)
        account_menu.addAction(logout_action)

        if self.api.is_admin:
            admin_menu = self.menuBar().addMenu("Администрирование")

            create_user_action = QAction("Создать пользователя", self)
            create_user_action.triggered.connect(self.open_create_user_window)
            admin_menu.addAction(create_user_action)

            change_role_action = QAction("Изменить роль пользователя", self)
            change_role_action.triggered.connect(self.open_change_role_window)
            admin_menu.addAction(change_role_action)

            security_policy_action = QAction("Политика безопасности", self)
            security_policy_action.triggered.connect(self.open_security_settings_window)
            admin_menu.addAction(security_policy_action)

            audit_action = QAction("Журнал аудита", self)
            audit_action.triggered.connect(self.open_audit_window)
            admin_menu.addAction(audit_action)

    def open_create_user_window(self) -> None:
        if not self.api.is_admin:
            QMessageBox.warning(self, "Доступ запрещен", "Создавать пользователей может только администратор.")
            return
        CreateUserWindow(self.api).exec()

    def open_change_role_window(self) -> None:
        if not self.api.is_admin:
            QMessageBox.warning(self, "Доступ запрещен", "Изменять роли может только администратор.")
            return
        ChangeRoleWindow(self.api).exec()

    def open_security_settings_window(self) -> None:
        if not self.api.is_admin:
            QMessageBox.warning(self, "Доступ запрещен", "Политика безопасности доступна только администратору.")
            return
        SecuritySettingsWindow(self.api).exec()

    def open_audit_window(self) -> None:
        if not self.api.is_admin:
            QMessageBox.warning(self, "Доступ запрещен", "Журнал аудита доступен только администратору.")
            return
        AuditWindow(self.api).exec()

    def _do_logout(self, *, show_errors: bool = False) -> None:
        if self._logout_sent or not self.api.token:
            return
        try:
            self.api.logout()
        except Exception as exc:
            if show_errors:
                QMessageBox.warning(self, "Выход", f"Не удалось зарегистрировать выход на сервере: {exc}")
        finally:
            self._logout_sent = True

    def _do_logout_and_close(self) -> None:
        self._do_logout(show_errors=True)
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._do_logout(show_errors=False)
        super().closeEvent(event)

    def change_password(self) -> None:
        ChangePasswordWindow(self.api).exec()

    def _double(self, value: float, minimum: float, maximum: float, decimals: int = 2, step: float = 1.0) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(minimum, maximum)
        box.setDecimals(decimals)
        box.setSingleStep(step)
        box.setValue(value)
        return box

    def payload(self) -> dict:
        return {
            "total_load": self.total_load.value(),
            "num_blocks": self.num_blocks.value(),
            "nominal_power_per_block": self.nominal_power.value(),
            "nominal_efficiency": self.nominal_efficiency.value(),
            "temp_c": self.temp_c.value(),
            "humidity": self.humidity.value(),
            "wind_speed": self.wind_speed.value(),
            "wind_dir": self.wind_dir.value(),
            "own_needs_coeff": self.own_needs.value(),
            "beta": self.beta.value(),
        }

    def run_calculation(self) -> None:
        try:
            self.last_result = self.api.run_calculation(self.payload())
            ResultsWindow(self.last_result).exec()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка расчета", str(exc))

    def show_charts(self) -> None:
        if not self.last_result:
            self.run_calculation()
        if self.last_result:
            ChartsWindow(self.last_result).exec()

    def export_csv(self) -> None:
        try:
            result = self.api.export_csv(self.payload())
            filename = result.get("filename", "CSV-файл")
            QMessageBox.information(
                self,
                "Экспорт",
                f"CSV создан на сервере: {filename}\n"
                "Файл доступен в каталоге exports серверной части.",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))

    def export_pptx(self) -> None:
        try:
            result = self.api.export_pptx(self.payload())
            filename = result.get("filename", "PPTX-файл")
            QMessageBox.information(
                self,
                "Экспорт",
                f"PPTX создан на сервере: {filename}\n"
                "Файл доступен в каталоге exports серверной части.",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))
