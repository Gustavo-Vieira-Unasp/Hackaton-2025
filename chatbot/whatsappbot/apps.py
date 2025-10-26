from django.apps import AppConfig
import os

class WhatsappbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "whatsappbot"

    def ready(self):
        if os.environ.get("RUN_MAIN") == "true":
            from .tasks import start_scheduler
            start_scheduler()
