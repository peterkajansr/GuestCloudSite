from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.views import redirect_to_login
from crm.forms import UserCreationForm



@login_required
def profile_home(request, username):
    if request.user.username != username:
        raise Http404()
    return render(request, 'crm/profile_home.html', {})

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
    
