from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from oauth2_provider.models import AbstractApplication
from django.contrib.auth import get_user_model

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, contact, password=None, **extra_fields):
        if not contact:
            raise ValueError('The contact field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, contact=contact, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, contact, password=None, **extra_fields):
        if not password:
            password = BaseUserManager.make_random_password()
    
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, first_name, last_name, contact, password, **extra_fields)


class User(AbstractBaseUser):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=300, unique=True)
    contact = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    dob = models.DateField()  # YYYY-MM-DD
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # For handling passwords securely
    password = models.CharField(max_length=150)

    # Custom manager for the User model
    objects = CustomUserManager()

    USERNAME_FIELD = 'contact'
    REQUIRED_FIELDS = ['first_name', 'last_name',]  # Fields required for creating a user

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
    
    def set_password(self, password):
        self.password = make_password(password)
        self.save()

    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser

class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    degree = models.CharField(max_length=100)
    university = models.CharField(max_length=100, blank=True)
    year_of_passing = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return f"{self.degree} from {self.university} (Year: {self.year_of_passing})"
    
"""class User(models.Model):

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length = 300, unique=True)
    contact = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    dob = models.DateField()                                              #YYYY-MM-DD
    address = models.TextField()
    password = models.CharField(max_length=150, default="")

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()

class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    university = models.CharField(max_length=100, blank=True)
    year_of_passing = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return f"{self.degree} from {self.university} (Year: {self.year_of_passing})"""
