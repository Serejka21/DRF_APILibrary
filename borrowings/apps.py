from django.apps import AppConfig


class BorrowingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings"

    def ready(self) -> None:
        """Connect signal handlers"""
        from . import signals
