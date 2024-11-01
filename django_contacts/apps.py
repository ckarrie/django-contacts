from django.apps import AppConfig


class DjangoContactsAppConfig(AppConfig):
    name = 'django_contacts'

    def ready(self):
        from django_contacts import models
        