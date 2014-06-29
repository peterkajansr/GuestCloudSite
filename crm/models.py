from django.db import models
from django.contrib.auth.models import AbstractUser
# from firebasein.firebase import Firebase


class User(AbstractUser):
    
    def save(self, *args, **kwargs):
#         firebase = Firebase('https://guestflow.firebaseio.com/')
#         print firebase.child('users')
        return super(User, self).save(*args, **kwargs)