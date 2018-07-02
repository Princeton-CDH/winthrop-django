from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'winthrop.common'

    def ready(self):
        # import and connect signal handlers for Solr indexing
        from winthrop.common.signals import IndexableSignalHandler

