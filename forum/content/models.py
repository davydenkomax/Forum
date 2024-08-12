from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.urls import reverse
from slugify import slugify
from django.utils import timezone
from .validators import check_max_size_file

# Create your models here.
class Section(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('content:subject_list_by_section', args=[self.slug])

class Subject(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Subject'
        verbose_name_plural = 'Subject'
        unique_together = ('id', 'slug')

    def __str__(self):
        return self.name  

    def get_absolute_url(self):
        return reverse('content:list_message_by_subject', args=[
            self.section.slug,
            self.id,
            self.slug
        ]) 

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs) 
    
class SubjectView(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='views'
    )
    date = models.DateField()
    views = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['date']

class Message(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='author_message',
        null=True
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='answer_messages',
        blank=True,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]

    def __str__(self):
        return f'Message form {self.author}'

class Content(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='messages',
        limit_choices_to={'model__in': ('text', 'video', 'image')}
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Text(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text

class Image(models.Model):
    file = models.FileField(upload_to='images', validators=[check_max_size_file])

class Video(models.Model):
    video = models.URLField()