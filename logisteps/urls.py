from django.urls import path

from . import views

app_name = 'logisteps'
urlpatterns = [
    path('', views.index, name='index')
]