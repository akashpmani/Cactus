from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password


class AccountsManager(BaseUserManager):

    def create_user(self, email, phone, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not phone:
            raise ValueError('The Phone field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone,
                          username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email=email, phone=phone, password=password,  username=username, **extra_fields)

    def authenticate(self, request, email=None, phone=None, password=None, username=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(Q(email=email) | Q(
                phone=phone) | Q(username=username))
        except UserModel.DoesNotExist:
            print('no user')
            return None
        else:
            if user and check_password(password, user.password):
                return user
        return None
    
    def getuser(self, request, email=None, phone=None, password=None, username=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(Q(email=email) | Q(
                phone=phone) | Q(username=username))
        except UserModel.DoesNotExist:
            return None
        return user

