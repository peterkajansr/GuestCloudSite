'''
Created on Jun 22, 2014

@author: pkajan
'''
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from crm.models import User
from django.forms import Form
from django.forms.fields import FileField

class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ("username",)


class ImportGuestsForm(Form):
    file = FileField()