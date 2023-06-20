from datetime import timedelta, timezone
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .models import User_Accounts,AddressBook,Profile,Country,Cart,State
from . forms import CustomerRegisterForm, Signin_Form , Otp_Form ,AddressBookForm
from django.contrib.auth import get_user_model
from django.contrib import messages,auth
from .manager import AccountsManager
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.utils import timezone
import random
from . import verify
from .otp import verify_otp
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
# from .helpers import delete_expired_otp
# Create your views here.

account_manager = AccountsManager()

def signup(request):
    if request.method == 'POST':
        signupform = CustomerRegisterForm(request.POST)
        if signupform.is_valid():
            signupform.save()
            return HttpResponse("signuedp ")
        else:
            print(signupform.errors)
            return HttpResponse("failed")

    form = CustomerRegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})



def signin(request):
    if request.method == 'POST':
        loginform = Signin_Form(request.POST)
        if loginform.is_valid():
            login_cred = loginform.cleaned_data['login_cred']
            password = loginform.cleaned_data['password']
            user = account_manager.authenticate(
                request, email=login_cred, phone=login_cred, username=login_cred, password=password)
            if user is not None:
                auth.login(request, user)
                return HttpResponse("login success")
            else:
                messages.error(request, 'Invalid login credentials')
                return HttpResponse('Invalid login credentials')
        else:
            return HttpResponse('form not valid')
    loginform = Signin_Form()
    return render(request, 'accounts/signin.html', {'form': loginform} )

def signinotp(request):
    if request.method == 'POST':
        login_cred = request.POST.get('login_cred')
        user = account_manager.getuser(
                request, email=login_cred, phone=login_cred, username=login_cred)
        if user is not None:
            request.session['email']=user.email
            verify.send(user.phone)
            otp_form = Otp_Form()
            return render(request, 'accounts/two_factorauth.html', {'form': otp_form , 'user' : user})          
        else:
            messages.error(request, 'Invalid login credentials')
            return HttpResponse('Invalid login credentials')
    return render(request, 'accounts/signinotp.html')

def otp(request):
    if request.method == 'POST':
        form = Otp_Form(request.POST)
        if form.is_valid():
            UserModel = get_user_model()
            code = form.cleaned_data['otp']
            user = UserModel.objects.get(email=request.session.get('email'))
            print(user.email)
            
            if verify.check(user.phone, code):
                messages.success(request, "OTP verified")
                auth.login(request, user)
                return HttpResponse("otp verified")
            else:

                error_msg = "Invalid OTP. Please try again later."
                messages.error(request, error_msg)
        else:
            messages.error(request, "Invalid OTP form submission. Please try again.")
    else:
        form = Otp_Form()
        
    return render(request, 'accounts/two_factorauth.html', {'form': form})



def  verifyemail(request):
    return render(request, 'accounts/verifyemail.html')

def profile(request):
    current_user = request.user
    if current_user.is_authenticated:
        user = User_Accounts.objects.get(username = current_user.username)
        country = Country.objects.all()
        states = State.objects.all()
        addressform = AddressBookForm()
        context = {
            'user' : user, 
            'states' : states,
            'country' : country,
            'addressform' : addressform,    
        }
        try:
            if Profile.objects.filter(user = user).exists:
                profile = Profile.objects.get(user = user)
                context['profile'] = profile
        except:
            pass
        
        try:
            if AddressBook.objects.filter(user = user).exists:
                address = AddressBook.objects.filter(user = user)
                context['address'] = address
        except:
            pass
        
      
        return render(request, 'accounts/profile.html',context)
    
    
    return redirect('accounts:signin')

def edit_address(request,id):
    address = get_object_or_404(AddressBook, id=id)
    if request.method == 'POST':
        form = AddressBookForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    return redirect('accounts:profile')

def delete_address(request,id):
    if request.method == 'POST':
        address =  AddressBook.objects.get(id = id)
        address.delete()
        return redirect('accounts:profile')
    
def add_address(request):
    if request.method == 'POST':
        form = AddressBookForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user 
            address.save()
        else:
            print(form.errors)
        return redirect('accounts:profile')
    

def update_password(request,id):    
    print("booom")
    if request.method == 'POST':
        try:
            user = User_Accounts.objects.get(id = id)
        except:
            pass
        old_password = request.POST.get('oldPassword')
        new_password = request.POST.get('newPassword')
        print(new_password)
        if user and check_password(old_password, user.password):
            print("yeasss")
            user.password = make_password(new_password)
            user.save()
            return JsonResponse({'message': 'Password update successful'})
        else:
            print("oombi")
            return JsonResponse({'message': 'invalid credentials'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)



    
    
    
    

  

