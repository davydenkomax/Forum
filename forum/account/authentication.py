from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.http import HttpRequest

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, username=None, password=None , **kwargs):
        try:
            user = User.objects.get(email=username)
            
            if user.check_password(password):
                return user
            else:
                return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user