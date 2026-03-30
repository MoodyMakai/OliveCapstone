"""QuartApp definition to stop pyright from complaining about StorageService."""

from quart import Quart

from src.email_service import EmailServiceProvider
from src.service import StorageService


class QuartApp(Quart):
    """A custom Quart application class with storage and email support.

    This class extends Quart to include storage and email service attributes
    for handling database operations, file storage, and email notifications.
    """

    storage: StorageService  # Define storage explicitly to stop pyright from complaining
    email_service: EmailServiceProvider  # Define email service for async notifications
