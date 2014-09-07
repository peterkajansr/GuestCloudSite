from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from crm.models import User, Guest, Invitation
from django.forms import Form
from django.forms.fields import FileField, EmailField
from django.forms.models import ModelForm, ModelChoiceField,\
    ModelMultipleChoiceField
from django.utils.translation import ugettext as _
from django.forms.widgets import CheckboxSelectMultiple
from django.core.exceptions import ValidationError

class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ("username",)


class ImportGuestsForm(Form):
    file = FileField()
    

class GuestForm(ModelForm):
    class Meta:
        model = Guest
        fields = '__all__'
        
        
class SelectGuestForm(Form):
    guests =  ModelMultipleChoiceField(queryset=(),
                  label=_('Select guests'),
                  widget=CheckboxSelectMultiple,
              )

    def __init__(self, guests_queryset, *args, **kwargs):        
        super(SelectGuestForm, self).__init__(*args, **kwargs)
        self.fields['guests'].queryset = guests_queryset
        if kwargs.get('data'):
            self.selected_guests = \
                [int(guest_id) for guest_id in kwargs['data'].getlist('guests')]
         
        
class InvitationForm(ModelForm):
    class Meta:
        model = Invitation
        fields = '__all__'
        labels = {
            'html_body': _('Html content'),
            'text_body': _('Plain text content'),
        }
        
        
class ChooseInvitationForm(Form):
    invitation =  ModelChoiceField(queryset=(),
                                   label=_("Choose message"))
    
    def __init__(self, messages_queryset, *args, **kwargs):        
        super(ChooseInvitationForm, self).__init__(*args, **kwargs)
        self.fields['invitation'].queryset = messages_queryset
        

class SendMessageForm(Form):
    from_email = EmailField(required=False)
    
    def clean_from_email(self):
        if not self.cleaned_data['from_email']:
            raise ValidationError(_('This field is required.'), code='required')

    

