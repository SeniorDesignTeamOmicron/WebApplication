from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError

from .models import Shoe, LogistepsUser

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Username', min_length=4, max_length=150)
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label="Firstname", max_length=50)
    last_name = forms.CharField(label="Lastname", max_length=50)
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    # shoe1 = forms.DecimalField(label='Left Shoe Size', min_value=4, max_value=16, max_digits=3, decimal_places=1)
    # shoe2 = forms.DecimalField(label='Right Shoe Size', min_value=4, max_value=16, max_digits=3, decimal_places=1)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        
        return password2
    
    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['first_name'],
            self.cleaned_data['last_name'],
            self.cleaned_data['password1']
        )
        # lShoe = Shoe.objects.create(foot='L', size=self.cleaned_data['shoe1'])
        # rShoe = Shoe.objects.create(foot='R', size=self.cleaned_data['shoe2'])

        # logistepsUser = LogistepsUser.objects.create(left_shoe=lShoe, right_shoe=rShoe, user=user)
        # lShoe.save()
        # rShoe.save()
        # logistepsUser.save()

        # return logistepsUser
        return user

# class UserCompletionForm(forms.Form):
