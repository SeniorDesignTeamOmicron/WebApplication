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
from utils.step_utils import getInactiveTime, getLeastActiveHour, getMostActiveHour, avgStepsPerHour

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

    def to12HourTime(self, twentyFourHourTime):
        if twentyFourHourTime == 0:
            return '12 AM'
        elif twentyFourHourTime <= 12:
            return str(twentyFourHourTime) + ' AM'
        else:
            return str(twentyFourHourTime - 12) + ' PM'

    def summarize(self, request, date, *args, **kwargs):
        queryset = Step.objects.all()

        logistepsUser = LogistepsUser.objects.get(user_id=self.request.user.id)

        if logistepsUser is not None:
            queryset = queryset.filter(user=logistepsUser.id,
                                       datetime__year=date.year,
                                       datetime__month=date.month,
                                       datetime__day=date.day)

        logistepsUser = LogistepsUser.objects.get(user_id=self.request.user.id)

        steps = queryset.count()
        goal = logistepsUser.step_goal

        most_active_hour = getMostActiveHour(queryset)
        least_active_hour = getLeastActiveHour(queryset)
        inactive_time = getInactiveTime(queryset)
        steps_per_hour = avgStepsPerHour(queryset, date)

        # do statistics here, e.g.
        stats = {
            'steps': steps,
            'least_active': self.to12HourTime(least_active_hour.get('datetime__hour')),
            'most_active': self.to12HourTime(most_active_hour.get('datetime__hour')),
            'inactive_time': inactive_time,
            'steps_per_hour': str(round(steps_per_hour, 2))
        }

        # not using a serializer here since it is already a 
        # form of serialization
        return stats

    def get(self, request, *args, **kwargs):
        today = datetime(2018, 8, 17)
        todaySum = self.summarize(request, today, *args, **kwargs)
        yesterdaSumy = self.summarize(request, today - timedelta(days=1), *args, **kwargs)

        return render(request, 'logisteps/recent.html', {'summary': {
            'today': todaySum,
            'yesterday': yesterdaSumy
        }})