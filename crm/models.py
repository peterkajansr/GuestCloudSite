from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    def save(self, *args, **kwargs):
        print "saving user"
        return super(User, self).save(*args, **kwargs)