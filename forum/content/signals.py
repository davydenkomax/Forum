from django.db.models.signals import post_save, post_delete
from .models import Section, Subject, Message
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Section)
def delete_cache_section(*agrs, **kwargs):
    cache.delete('section_list')

@receiver([post_save, post_delete], sender=Subject)
def delete_cach_subject(sender, instance, *agrs, **kwargs):
    cache.delete(f'subject_list:{instance.section.id}')

@receiver([post_save, post_delete], sender=Message)
def delete_cache_message(sender, instance, *agrs, **kwargs):
    cache.delete(f'message_list:{instance.subject.id}:{instance.subject.slug}')