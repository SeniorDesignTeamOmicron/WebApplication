from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic import View

from .forms import CustomUserCreationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            return redirect('logisteps:index')

    else:
        f = CustomUserCreationForm()

    return render(request, 'logisteps/register.html', {'form': f})

@method_decorator(login_required, name='dispatch')
class ProtectedView(TemplateView):
    template_name = 'secret.html'

class IndexView(ProtectedView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'logisteps/index.html')