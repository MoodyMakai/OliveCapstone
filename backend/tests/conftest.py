import pytest

from src.app import app


@pytest.fixture(name="test_app", scope="function")
async def fixture_test_app():
    # Configure to use an in memory database
    test_db_name = ":memory:"
    app.config["DB_PATH"] = test_db_name

    async with app.test_app() as test_client:
        yield test_client


@pytest.fixture(name="client")
async def fixture_client(test_app):
    return test_app.test_client()
