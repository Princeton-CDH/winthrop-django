import logging

from django.db import models

from winthrop.common.solr import Indexable


logger = logging.getLogger(__name__)


class IndexableSignalHandler:

    index_within = 3

    index_params = {'commitWithin': index_within * 1000}

    connected = False

    def handle_save(sender, instance, **kwargs):
        if isinstance(instance, Indexable):
            logger.debug('Indexing %r', instance)
            instance.index(params=IndexableSignalHandler.index_params)

    def handle_delete(sender, instance, **kwargs):
        logger.debug('Deleting %r from index', instance)
        if isinstance(instance, Indexable):
            instance.remove_from_index(params=IndexableSignalHandler.index_params)

    def handle_relation_change(sender, instance, action, **kwargs):
        # handle add, remove, and clear for indexable instances
        if action in ['post_add', 'post_remove', 'post_clear']:
            if isinstance(instance, Indexable):
                logger.debug('Indexing %r (m2m change)', instance)
                instance.index(params=IndexableSignalHandler.index_params)

    def connect():
        '''bind indexing signal handlers to save and delete signals for
        :class:`~ppa.archive.solr.Indexable` subclassess and any
        indexing dependencies'''

        # bind to save and delete signals for indexable subclasses
        for model in Indexable.__subclasses__():
            logger.debug('Registering signal handlers for %s', model)
            models.signals.post_save.connect(IndexableSignalHandler.handle_save, sender=model)
            models.signals.post_delete.connect(IndexableSignalHandler.handle_delete, sender=model)

        Indexable.identify_index_dependencies()
        for m2m_rel in Indexable.m2m:
            logger.debug('Registering m2m signal handler for %s', m2m_rel)
            models.signals.m2m_changed.connect(IndexableSignalHandler.handle_relation_change,
                                               sender=m2m_rel)

        for model, options in Indexable.related.items():
            for model_signal in ['pre_save', 'post_save', 'pre_delete', 'post_delete']:
                if model_signal in options:
                    signal = getattr(models.signals, model_signal)
                    logger.debug('Registering %s signal handler for %s', model_signal, model)
                    signal.connect(options[model_signal], sender=model)


    def disconnect():
        '''disconnect indexing signal handlers'''
        for model in Indexable.__subclasses__():
            logger.debug('Disconnecting signal handlers for %s', model)
            models.signals.post_save.disconnect(IndexableSignalHandler.handle_save, sender=model)
            models.signals.post_delete.disconnect(IndexableSignalHandler.handle_delete, sender=model)

        for m2m_rel in Indexable.m2m:
            logger.debug('Disconnecting m2m signal handler for %s', m2m_rel)
            models.signals.m2m_changed.disconnect(IndexableSignalHandler.handle_relation_change,
                                                  sender=m2m_rel)

        for model, options in Indexable.related.items():
            if 'save' in options:
                logger.debug('Disconnecting save signal handler for %s', model)
                models.signals.pre_save.disconnect(options['save'], sender=model)
            if 'delete' in options:
                logger.debug('Disconnecting delete signal handler for %s', model)
                models.signals.pre_delete.disconnect(options['delete'], sender=model)



IndexableSignalHandler.connect()
