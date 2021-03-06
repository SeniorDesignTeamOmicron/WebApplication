from django.urls import path
from . import views

app_name = 'logisteps'
urlpatterns = [
    path('', views.RecentView.as_view(), name='recent'),
    path('register/', views.register, name='register'),
    path('profile/complete/', views.completeProfile, name='complete_profile'),
    path('profile/update/', views.updateProfile, name='update_profile'),
    path('recent', views.RecentView.as_view(), name='recent'),
    path('steps_over_time', views.StepsOverTime.as_view(), name='steps_over_time'),
    path('steps_by_day', views.StepsByDay.as_view(), name='steps_by_day'),
    path('activity', views.Activity.as_view(), name='activity'),
    path('pressure', views.PressureView.as_view(), name='pressure'),
    path('map', views.MapView.as_view(), name='map')
]