from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField

class User(AbstractUser):
    
    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)
    
    
class Guest(Model):
    first_name = CharField(max_length=50, default='')
    last_name = CharField(max_length=50, default='')
    custom1 = CharField(max_length=256, default='')
    custom2 = CharField(max_length=256, default='')
    note = CharField(max_length=1024, default='')
    
    @classmethod
    def list(cls, user, event):
        cls.objects.all()       # TODO by user and event
    
    