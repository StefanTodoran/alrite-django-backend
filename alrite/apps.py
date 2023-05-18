from django.apps import AppConfig
from django.db.backends.signals import connection_created
import threading

first_connection = threading.Semaphore()
def on_connection_created(**kwargs):
    if first_connection.acquire(blocking=False):
        from .custom_models import on_startup
        on_startup()

class AlriteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alrite'

    #def ready(self):
        #connection_created.connect(on_connection_created)
