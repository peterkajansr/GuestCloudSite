'''
Created on Jun 22, 2014

@author: pkajan
'''
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from crm.models import User

class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
