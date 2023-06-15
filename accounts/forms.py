from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User_Accounts,AddressBook
from django.core.exceptions import ValidationError
import re
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


def validate_phone_number(value):
    # Define a regular expression pattern to match phone numbers with country code
    pattern = r'^\+\d{1,3}\d{9,10}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Please enter a phone number with country code, e.g. +91xxxxxxxxxx')


class CustomerRegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True,
                            help_text='Phone number', validators=[validate_phone_number])
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(required=False)
    STATUS_CHOICES = (
    ('active', 'Active'),
    ('suspended', 'Suspended'),
    ('blocked', 'Blocked'),
)

    status = forms.ChoiceField(choices=STATUS_CHOICES, label='Status', required=False, initial='active')


    class Meta:
        model = User_Accounts
        fields = ['email', 'phone', 'username', 'password1']
        widget = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
                'maxlength': '10',
                'minlength': '10',
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),

        }


class Signin_Form(forms.Form):
    login_cred = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class Otp_Form(forms.Form):
    otp = forms.CharField()
    
    

class AddressBookForm(forms.ModelForm):
    class Meta:
        model = AddressBook
        fields = ['first_name', 'last_name', 'phone', 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'pincode', 'default']
    