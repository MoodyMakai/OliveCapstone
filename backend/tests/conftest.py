import pytest

from src.app import app
from src.database import DatabaseManager
from src.service import StorageService
from src.storage import LocalFileStorage


@pytest.fixture(name="test_app", scope="function")
async def fixture_test_app():
    # Configure to use an in memory database
    app.config["DB_PATH"] = ":memory:"

    async with app.test_app() as test_app:
        yield test_app
    await app.shutdown()


@pytest.fixture(name="client")
async def fixture_client(test_app):
    return test_app.test_client()


@pytest.fixture(name="db_manager")
async def fixture_database_manager():
    manager = DatabaseManager(":memory:")
    await manager.connect()
    await manager.init_tables()
    yield manager
    await manager.close()


@pytest.fixture(name="storage_service")
async def storage_service(db_manager: DatabaseManager, tmp_path):
    storage = LocalFileStorage(upload_folder=str(tmp_path))
    service = StorageService(db=db_manager, storage=storage)
    yield service
    await service.close()
