from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import EmailValidator, RegexValidator

class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier for authentication.
    """
    def create_user(self, email, password=None, first_name="", last_name="",  phone_number= "", **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        email_validator = EmailValidator()
        email_validator(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password,  first_name="", last_name="",  phone_number= "", **extra_fields):
        """
        Create and save a Superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, first_name, last_name, phone_number, **extra_fields)
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model where email is the unique identifier and required field.
    """
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True, validators=[EmailValidator()])
    phone_number = models.CharField(_('phone number'), max_length=100, blank=True, null=True, unique=True, help_text=_('Up to 100 digits allowed.'))
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(_('profile picture'), upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(_('biography'), blank=True)
    gender = models.CharField(_('gender'), max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True)
    preferences = models.JSONField(_('preferences'), default=dict, blank=True, help_text=_('JSON field to store user preferences such as favorite genres, actors, etc.'))
    location = models.CharField(_('location'), max_length=255, blank=True, help_text=_('User location, can be used for regional recommendations.'))
    groups = models.ManyToManyField(
        'auth.Group', related_name='customuser_set', related_query_name='customuser',
        blank=True, help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        verbose_name=_('groups'))
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='customuser_set', blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        app_label = 'accounts'
        db_table = 'custom_user'

    def __str__(self):
        return f'{self.email}'