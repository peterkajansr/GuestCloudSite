import csv 
from io import TextIOWrapper
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from crm.forms import UserCreationForm, ImportGuestsForm, GuestForm,\
    ChooseInvitationForm, InvitationForm, SendMessageForm, SelectGuestForm
from crm.models import Guest, Invitation
from django.core.mail.message import EmailMultiAlternatives
from django.core import mail as django_mail
from django.template import Template, Context
# from firebasein.firebase import Firebase

def own_profile(function):
    """ ensures that username parsed from url matches 
        username of the logged user """
    def wrapped(request, *args, **kwargs):
        username = kwargs.pop('username')
        if request.user.username != username:
            raise Http404()  
        return function(request, *args, **kwargs)
    wrapped.__name__ = function.__name__
    return wrapped


@login_required
@own_profile
def profile_home(request):
    return render(request, 'crm/profile_home.html', {})


def handle_uploaded_file(the_file, request):
    f = TextIOWrapper(the_file.file, encoding=request.encoding)
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        attrs = {}
        colums_cnt = len(row)
        for i, guest_attr in enumerate(
                ['first_name', 'last_name', 'email', 'custom1', 'custom2', 'note']):
            if i >= colums_cnt:
                break
            attrs[guest_attr]=row[i].strip()
        
        Guest.objects.create(**attrs)
        

@login_required
@own_profile
def import_guest(request):
    if request.method == 'POST':
        form = ImportGuestsForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'],request)
            return HttpResponseRedirect(reverse('crm:guests', 
                                                kwargs={'username': request.user.username}))
    else:
        form = ImportGuestsForm()
        
    return render(request, 'crm/import.html', {
       'form': form,
    })
    
@login_required
@own_profile
def guests(request):        
    if request.method == 'POST':
        if 'delete' in request.POST:
            guest_ids = request.POST.getlist('guests')
            Guest.delete(guest_ids)
            
    return render(request, 'crm/guests.html', {
       'guests' : Guest.list(request.user, 'actual_event'),
    })

    
@login_required
@own_profile
def guest_detail(request, guest_id):        
    guest = get_object_or_404(Guest, pk=guest_id)
    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            if 'cancel' not in request.POST:
                form.save()
            
            return HttpResponseRedirect(reverse('crm:guests', 
                                                kwargs={'username': request.user.username})) 
    else:
        form = GuestForm(instance=guest)
    
    return render(request, 'crm/guest_detail.html', {
        'form': form,
    })


def fill_template(template_str, context_data):
    template = Template(template_str)
    context = Context(context_data)
    return template.render(context)


def _send_message(guest_id, message, connection):
    guest = Guest.objects.get(pk=int(guest_id))
    
    message_data = {
        'name': guest.first_name,
    }
    html_message = fill_template(message.html_body, message_data)
    plain_text = fill_template(message.text_body, message_data)
    
    msg = EmailMultiAlternatives(
        subject=message.subject,
        body=plain_text, 
        from_email = message.from_email,
        to=(guest.email,),
        connection=connection,
    )
                                 
    msg.attach_alternative(html_message, "text/html")
    msg.content_subtype = "html"
    msg.send()
    
    return msg.connection


def _send_messages(guest_ids, send_form_data, messages_form_data):
    message = messages_form_data['invitation']
    message.from_email = send_form_data['from_email']
    
    connection = django_mail.get_connection()
    
    for guest_id in guest_ids:
        try:
            _send_message(guest_id, message, connection)
        except Exception as e:
            # TODO error handling
            print(e)
        
    connection.close()
        

def _create_choose_message_form(request, data=None):
    return  ChooseInvitationForm(
        messages_queryset = Invitation.list(), 
        data = data,
    )

def _create_send_form(request, data=None):
    return SendMessageForm(
        initial = {'from_email': request.user.username + '@guestcloud.sk'},
        data = data,
    )
    
def _create_guests_form(request, data=None):
    return SelectGuestForm(
        guests_queryset=Guest.list(request.user, 'actual_event'),
        data=data,
    )
    
@login_required
@own_profile
def invitations(request):        
    template_params = {}
    send_form = None
    messages_form = None
    guests_form = None
    
    if request.method == 'POST':
        messages_form = _create_choose_message_form(request, request.POST)
        guests_form = _create_guests_form(request, request.POST)
        
        if 'invite' in request.POST:
            send_form = _create_send_form(request, request.POST)
            if messages_form.is_valid() and send_form.is_valid() \
            and guests_form.is_valid():
                _send_messages(guests_form.selected_guests, 
                               send_form.cleaned_data,
                               messages_form.cleaned_data)
                template_params['sent'] = True
        elif 'delete' in request.POST:
            if messages_form.is_valid():
                messages_form.cleaned_data['invitation'].delete()
                template_params['deleted'] = True
        elif 'edit' in request.POST:
            if messages_form.is_valid():
                return HttpResponseRedirect(
                    reverse('crm:invitation_edit', 
                            kwargs={'username': request.user.username,
                                    'invitation_id': messages_form.cleaned_data['invitation'].pk}))
    
    if not messages_form:
        messages_form = _create_choose_message_form(request)
        
    if not send_form:
        send_form = _create_send_form(request)
        
    if not guests_form:
        guests_form = _create_guests_form(request)
    
    template_params['choose_message_form'] = messages_form 
    template_params['send_form'] = send_form
    template_params['guests_form'] = guests_form
    template_params.setdefault('guests', Guest.list(request.user, 'actual_event'))
    template_params.setdefault('mails', Invitation.list())
    
    return render(request, 'crm/invitations.html', template_params)
    
@login_required
@own_profile
def invitation_edit(request, invitation_id):        
    guest = get_object_or_404(Invitation, pk=invitation_id)
    if request.method == 'POST':
        form = InvitationForm(request.POST, instance=guest)
        if form.is_valid():
            if 'cancel' not in request.POST:
                form.save()
            
            return HttpResponseRedirect(reverse('crm:invitations', 
                                                kwargs={'username': request.user.username})) 
    else:
        form = InvitationForm(instance=guest)
    
    return render(request, 'crm/invitation_detail.html', {
        'form': form,
    })
    
    
@login_required
@own_profile
def invitation_create(request):        
    invitation = Invitation()
    if request.method == 'POST':
        form = InvitationForm(request.POST, instance=invitation)
        if form.is_valid():
            if 'cancel' not in request.POST:
                form.save()
            
            return HttpResponseRedirect(
                reverse('crm:invitations', 
                    kwargs={
                        'username': request.user.username,
                    })) 
    else:
        form = InvitationForm(instance=invitation)
    
    return render(request, 'crm/invitation_detail.html', {
        'form': form,
        'create': True
    })
    
@login_required
@own_profile
def invitation_preview(request, invitation_id):        
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    return HttpResponse(invitation.html_body)
    
    
@login_required
@own_profile
def guestflow(request):
    return render(request, 'crm/guestflow.html', {})


@login_required
def profile_redirect(request):
    return HttpResponseRedirect(reverse('crm:profile_home', 
                                 kwargs={'username': request.user.username}))
    
def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('crm:profile_redirect'))
    
    return render(request, 'registration/register.html', {'form': form})


