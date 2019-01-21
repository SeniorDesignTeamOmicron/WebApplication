from django.conf.urls import url
from django.urls import path
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
app_name = 'logisteps_api'

urlpatterns = [
    path('location/', views.LocationList.as_view()),
    path('location/<int:pk>/', views.LocationDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('user/', views.UserCreate.as_view()),
    path('user/<str:user__username>/', views.LogistepsUserDetail.as_view()),
    path('steps/', views.StepList.as_view()),
    path('steps/steplist/', views.StepsListByDay.as_view()),
    path('steps/summary/', views.StepSummary.as_view(), name='summary'),
    path('steps/count/', views.StepCount.as_view(), name='step_count'),
    path('steps/breakdown/', views.StepsBreakdown.as_view(), name='breakdown')
]

urlpatterns = format_suffix_patterns(urlpatterns)