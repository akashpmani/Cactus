from django.shortcuts import render
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import User_Accounts
from . forms import  Otp_Form
from django.contrib.auth import get_user_model
from .manager import AccountsManager
from . import verify



def verify_otp(request):
    print('in otp')
    if request.method == 'POST':
        form = Otp_Form(request.POST)
        if form.is_valid():
            UserModel = get_user_model()
            code = form.cleaned_data['otp']
            user = UserModel.objects.get(email=request.session.get('email'))
            
            print(user.email)
            
            if verify.check(user.phone_number, code):
                return True
            else:
                return False
    else:        
        form = Otp_Form()
    return render(request, 'accounts/two_factorauth.html', {'form': form})