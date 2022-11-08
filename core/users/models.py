from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

from uuid import uuid4


class UserManager(BaseUserManager):   
    def create_user(self, email, username, password=None, **kwargs):
        """
        Creates and saves a User with the given email and password.
        **kwargs: other fields from User model including those inherited from Users's parent class PermissionsMixin.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **kwargs
        )

        # user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **kwargs):
        """
        Creates and saves a superuser with the given email and password.
        **kwargs: f other fields from User model including those inherited from Users's parent class PermissionsMixin.
        """
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if not kwargs.get('is_superuser'):
            raise ValueError('Superuser must have is_staff field set to True')
        
        if not kwargs.get('is_active'):
            raise ValueError('Superuser must have is_superuser field set to True')

        user = self.create_user(
            email,
            username,
            password=password,
            **kwargs
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    
    username = models.CharField(_('username'), max_length=32, unique=True)

    created_at = models.DateField(_('created at'), default=timezone.now)
    updated_at = models.DateField(_('updated at'), auto_now=True)
    last_login = models.DateField(_('last login'), null=True)
    last_logout = models.DateField(_('last logout'), null=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    # used as a login
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    # required for the creation of superuser
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # All admins are staff
        return self.is_admin


class UserPersonalProfile(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # blank: validation related
    first_name = models.CharField(_('first name'), max_length=64, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=64, null=True, blank=True)
