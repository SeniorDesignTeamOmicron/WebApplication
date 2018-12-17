from django.urls import path
from . import views

app_name = 'logisteps'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('register/', views.register, name='register'),
    path('profile/complete/', views.CompleteProfile.as_view())
]