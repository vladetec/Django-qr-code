from django.apps import AppConfig
from django.core.management import call_command

class ShortenerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shortener'
    
    def ready(self):
        call_command('makemigrations')
        call_command('migrate')