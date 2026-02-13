import os

import pytest

from src.app import app


@pytest.fixture(name="test_app", scope="function")
async def fixture_test_app():
    # 1. Configure app to use a temporary test DB
    test_db_name = ":memory:"
    app.config["DB_PATH"] = test_db_name

    # 2. Yield the app (Quart handles startup/shutdown hooks automatically in tests)
    async with app.test_app() as test_client:
        yield test_client

    # 3. Cleanup: The shutdown hook has run, so we can delete the file
    if os.path.exists(test_db_name):
        os.remove(test_db_name)


@pytest.fixture(name="client")
async def fixture_client(test_app):
    return test_app.test_client()
