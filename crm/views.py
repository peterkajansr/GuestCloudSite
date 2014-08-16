from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from crm.forms import UserCreationForm
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
    
