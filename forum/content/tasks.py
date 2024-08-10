from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Message, Subject, SubjectView
from redis import Redis
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

r = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

@shared_task
def task_send_mail(user_id, parent_message_id):
    user = User.objects.get(id=user_id)
    parent_message = Message.objects.get(id=parent_message_id)
    
    subject = 'На ваше сообщение ответил пользователь форума'
    text = f'На ваше сообщение ответил {user}'
    
    if user.first_name and user.last_name:
        text = f'На ваше сообщение ответил {user.first_name} {user.last_name}'

    send_mail(
        subject=subject,
        message=text,
        from_email='django.project.forum@gmail.com',
        recipient_list=[parent_message.author.email]
    )

@shared_task
def set_count_views():
    subjects = Subject.objects.filter(active=True)

    for subject in subjects:
        views = r.get(f'subject:{subject.id}:views')

        if not views:
            views = 0

        subject_views = SubjectView.objects.filter(subject=subject)
        
        if subject_views:
            last_views = 0
            for subject_views_last in subject_views:
                last_views += subject_views_last.views
  
            views = int(views) - last_views
        
        SubjectView.objects.create(
            subject=subject,
            date=timezone.now(),
            views=views
        )

        cache.delete(f'subject_views:{subject.id}')