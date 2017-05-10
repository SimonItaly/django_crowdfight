
# -*- coding: utf-8 -*-

'''
    Crowdfight is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Crowdfight is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    Developed in Python by:
            - Bisi Simone    [ bisi.simone (at) gmail (dot) com ]
    for studying purposes ONLY on year 2017.
'''

import re

from django import forms
from django.contrib.auth.models import User

from .models import *

class RegistrationForm(forms.Form):
 
    username =  forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label="Username", error_messages={ 'invalid': "Questo campo può contenere solo lettere, numeri e underscore." })
    email =     forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label="Email")
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password (ripeti)")
 
    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("Questo username è già in uso.")
 
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Le password inserite non coincidono.")
        return self.cleaned_data

#-------------------------------------------------------------------------------

class LoginForm(forms.Form):

    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label="Username")
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")

#-------------------------------------------------------------------------------

class ImageUploadForm(forms.Form):
    title = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label="Nome")
    image = forms.ImageField(label="Immagine")
