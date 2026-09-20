from django.apps import AppConfig

class SupportConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'support'
    def ready(self):
        import support.signals  # noqa: F401
