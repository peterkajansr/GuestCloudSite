import csv
from io import TextIOWrapper
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from crm.forms import UserCreationForm, ImportGuestsForm, GuestForm,\
    ChooseInvitationForm, InvitationForm
from crm.models import Guest, Invitation
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

@login_required
@own_profile
def invitations(request):        
    template_params = {}
    form = None
    if request.method == 'POST':
        form = ChooseInvitationForm(request.POST)
        if form.is_valid():
            if 'invite' in request.POST:
                template_params['sent'] = True
            elif 'delete' in request.POST:
                form.cleaned_data['invitation'].delete()
                template_params['deleted'] = True
            elif 'edit' in request.POST:
                return HttpResponseRedirect(
                    reverse('crm:invitation_edit', 
                            kwargs={'username': request.user.username,
                                    'invitation_id': form.cleaned_data['invitation'].pk}))

    template_params.setdefault('form', form if form else ChooseInvitationForm())
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
    return HttpResponse(invitation.message)
    
    
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


