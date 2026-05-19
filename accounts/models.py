from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from accounts.managers import UserManager
from cloudinary.models import CloudinaryField

class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        READER = 'reader', 'Reader'
        JOURNALIST = 'journalist', 'Journalist'
        EDITOR = 'editor', 'Editor'
        ADMIN = 'admin', 'Admin'
        SUPERADMIN = 'superadmin', 'Super Admin'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = CloudinaryField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.READER)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_reader(self):
        return self.role == self.Roles.READER
    
    @property
    def is_journalist(self):
        return self.role == self.Roles.JOURNALIST
    
    @property
    def is_editor(self):
        return self.role == self.Roles.EDITOR
    
    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN
    
    @property
    def is_superadmin(self):
        return self.role == self.Roles.SUPERADMIN
    
    
