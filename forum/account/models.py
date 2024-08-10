from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    photo = models.FileField(
        upload_to='photo_profiles',
        default='photo_profiles/default.jpg'
    )

    def __str__(self):
        return f'Profie of {self.user}'