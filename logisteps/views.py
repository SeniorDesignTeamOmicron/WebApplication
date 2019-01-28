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
from datetime import datetime, timedelta

from .models import LogistepsUser, Step
from .forms import CustomUserCreationForm, UserCompletionForm
from utils.step_utils import getInactiveTime, getLeastActiveHour, getMostActiveHour, avgStepsPerHour, getDateSummary
from utils.helper import to12HourTime

# Create your views here.
def register(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            user = f.save()

            login(request, user)
            return redirect('/logisteps/profile/complete/')

    else:
        f = CustomUserCreationForm()

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
    
    def formatResponse(self, data):
        print(data.get('least_active_hour'))
        stats = {
            'steps': data.get('steps'),
            'least_active': to12HourTime(data.get('least_active').get('hour')),
            'most_active': to12HourTime(data.get('most_active').get('hour')),
            'inactive_time': data.get('inactive_time'),
            'steps_per_hour': str(round(data.get('steps_per_hour'), 2))
        }

        return stats

    def summarize(self, request, *args, **kwargs):
        today = datetime(2018, 8, 17)

        todaySum = getDateSummary(request.user, today)
        yesterdaySum = getDateSummary(request.user, today - timedelta(days=1))

        todaySum = self.formatResponse(todaySum)
        yesterdaySum = self.formatResponse(yesterdaySum)

        return {
            'today': todaySum,
            'yesterday': yesterdaySum
        }

    def get(self, request, *args, **kwargs):
        data = self.summarize(request)

        return render(request, 'logisteps/recent.html', {'summary': data})

class StepsOverTime(ProtectedView):
    template_name = 'steps_over_time.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'logisteps/steps_over_time.html')

class StepsByDay(ProtectedView):
    template_name = 'steps_by_weekday.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'logisteps/steps_by_weekday.html')

class Activity(ProtectedView):
    template_name = 'activity.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'logisteps/activity.html')