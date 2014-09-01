import csv
from io import TextIOWrapper
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from crm.forms import UserCreationForm, ImportGuestsForm, GuestForm
from crm.models import Guest
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
        Guest.objects.create(
            first_name = row[0],
            last_name = row[1],
            email = row[2],
        )
        

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
    return render(request, 'crm/guests.html', {
       'guests' : Guest.list(request.user, 'actual_event'),
    })

    
@login_required
@own_profile
def guest_detail(request, guest_id):        
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('crm:guests', 
                                                kwargs={'username': request.user.username})) 
    else:
        guest = get_object_or_404(Guest, pk=guest_id)
        form = GuestForm(instance=guest)
    
    return render(request, 'crm/guest_detail.html', {
        'form': form,
    })


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
    
