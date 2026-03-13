"""QuartApp definition to stop pyright from complaining about StorageService."""

from quart import Quart

from src.service import StorageService


class QuartApp(Quart):
    """A custom Quart application class with storage support.

    This class extends Quart to include a storage attribute for handling
    database operations and file storage.
    """

    storage: StorageService  # Define storage explicitly to stop pyright from complaining
