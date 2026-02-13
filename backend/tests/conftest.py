import pytest

from src.app import app
from src.database import DatabaseManager


@pytest.fixture(name="test_app", scope="function")
async def fixture_test_app():
    # Configure to use an in memory database
    app.config["DB_PATH"] = ":memory:"

    async with app.test_app() as test_client:
        yield test_client
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
