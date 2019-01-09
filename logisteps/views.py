from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib.auth import views as auth_views
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic import View

from .models import LogistepsUser
from .forms import CustomUserCreationForm, UserCompletionForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            user = f.save()

            login(request, user)
            print('Form is valid')
            return redirect('/logisteps/profile/complete/')

    else:
        f = CustomUserCreationForm()
        print("Form not valid")

    return render(request, 'logisteps/register.html', {'form': f})

@method_decorator(login_required, name='dispatch')
class ProtectedView(TemplateView):
    template_name = 'secret.html'

class IndexView(ProtectedView):
    template_name = 'index.html'

    # def dispatch(self, request, *args, **kwargs):
    #     # parse the request here ie.
    #     self.logistepsUser = request.GET.get('user', None)
    #     print(self.logistepsUser)

    #     # call the view
    #     return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'logisteps/index.html')

@login_required
def completeProfile(request):
    if request.method == 'POST':
        f = UserCompletionForm(request.user, request.POST)
        if f.is_valid():
            f.save()

            return redirect('/logisteps/')

    else:
        f = UserCompletionForm(request.user)

    return render(request, 'logisteps/complete_profile.html', {'form': f})

class RecentView(ProtectedView):
    template_name = 'recent.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'logisteps/recent.html')