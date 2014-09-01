from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField
from django.db.models.fields import EmailField

class User(AbstractUser):
    
    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)
    
    
class Guest(Model):
    first_name = CharField(max_length=50, default='')
    last_name = CharField(max_length=50, default='')
    email = EmailField(default='')
    custom1 = CharField(max_length=256, default='', blank=True)
    custom2 = CharField(max_length=256, default='', blank=True)
    note = CharField(max_length=1024, default='', blank=True)
    
    @classmethod
    def list(cls, user, event):
        return cls.objects.all()       # TODO by user and event
    
    @classmethod
    def delete(cls, guest_ids):
        ids = [int(the_id) for the_id in guest_ids]
        return cls.objects.filter(id__in=ids).delete()
    
    