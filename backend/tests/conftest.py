import secrets

import pytest

from src.app import app as quart_app
from src.database import DatabaseManager
from src.database_helpers import hash_token
from src.service import StorageService
from src.storage import LocalFileStorage


class AuthClient:
    """A wrapper around the Quart test client that automatically adds auth headers."""

    def __init__(self, client, token):
        self.client = client
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def _add_auth(self, kwargs):
        headers = kwargs.get("headers", {}).copy()
        headers.update(self.headers)
        kwargs["headers"] = headers
        return kwargs

    async def get(self, *args, **kwargs):
        return await self.client.get(*args, **self._add_auth(kwargs))

    async def post(self, *args, **kwargs):
        return await self.client.post(*args, **self._add_auth(kwargs))

    async def put(self, *args, **kwargs):
        return await self.client.put(*args, **self._add_auth(kwargs))

    async def delete(self, *args, **kwargs):
        return await self.client.delete(*args, **self._add_auth(kwargs))

    async def patch(self, *args, **kwargs):
        return await self.client.patch(*args, **self._add_auth(kwargs))


@pytest.fixture(name="test_app", scope="function")
async def fixture_test_app():
    # Configure to use an in memory database
    quart_app.config["DB_PATH"] = ":memory:"

    async with quart_app.test_app() as test_app:
        yield test_app
    await quart_app.shutdown()


@pytest.fixture(name="client")
async def fixture_client(test_app):
    return test_app.test_client()


@pytest.fixture(name="authenticated_client")
async def fixture_authenticated_client(test_app):
    """Provides an AuthClient for a regular verified user."""
    client = test_app.test_client()
    email = "testuser@maine.edu"

    # Create user and session directly in the app's database
    db = quart_app.storage.db
    user_id = await db.add_user(email, verified=True)
    assert user_id

    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    await db.create_device_token(user_id, token_hash)

    return AuthClient(client, raw_token)


@pytest.fixture(name="admin_client")
async def fixture_admin_client(test_app):
    """Provides an AuthClient for an admin user."""
    client = test_app.test_client()
    email = "admin@maine.edu"

    db = quart_app.storage.db
    # Create user and manually set is_admin
    user_id = await db.add_user(email, verified=True)
    assert user_id
    await db.conn.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    await db.conn.commit()

    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    await db.create_device_token(user_id, token_hash)

    return AuthClient(client, raw_token)


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


@pytest.fixture
def temp_upload_dir(tmp_path):
    return str(tmp_path / "uploads")


@pytest.fixture
def storage(temp_upload_dir):
    return LocalFileStorage(temp_upload_dir)
