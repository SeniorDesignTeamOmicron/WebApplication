from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from . import views

app_name = 'logisteps'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('register/', views.register, name='register')
]