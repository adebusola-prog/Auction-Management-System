from .managers import CustomUserManager, IsActiveManager, IsDeletedManager
from django.db import models

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    deleted_objects = IsDeletedManager()
    active_objects = IsActiveManager()

    class Meta:
        abstract = True
        ordering = ['-created_date']