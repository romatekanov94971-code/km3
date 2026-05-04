import pytest

from app.common.schemas import CalculationInput
from app.calculation.orchestrator import run_full_calculation
from app.server.config import get_settings
from app.storage.database import init_db
from app.storage.repositories import CalculationRepository, UserRepository
from app.auth.service import hash_password


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "audit.log"))
    get_settings.cache_clear()
    init_db()
    yield
    get_settings.cache_clear()


def test_user_and_calculation_history_storage():
    user = UserRepository().create_user("admin", hash_password("Admin123!"), "admin")
    data = CalculationInput(400, 2, 300, 0.38, 25, 60, 3, 90)
    result = run_full_calculation(data).to_dict()
    repo = CalculationRepository()
    record_id = repo.create(user.id, data.to_dict(), result)
    rows = repo.list_for_user(user.id)
    assert rows[0]["id"] == record_id
    assert rows[0]["result"]["main_result"]["fuel_consumption"] > 0
