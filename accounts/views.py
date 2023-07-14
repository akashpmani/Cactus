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
from orders.models import Order,OrderProduct,Payment
from django.db import transaction
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
        orders = Order.objects.filter(user = request.user).exclude(status="New").order_by('-created_at')
        context = {
            'user' : user, 
            'states' : states,
            'country' : country,
            'addressform' : addressform, 
            'orders' : orders,   
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
        try:
            if AddressBook.objects.filter(user = user , default = True).exists:
                print("dfs")
                d_address = AddressBook.objects.get(user = user ,default = True)
                print(d_address)
                context['d_address'] = d_address
        except:
            pass
        
      
        return render(request, 'accounts/profile1.html',context)
    
    
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
    address =  AddressBook.objects.get(id = id)
    address.delete()
    return redirect('accounts:addressbook')
    
def add_address(request):
    if request.method == 'POST':
        form = AddressBookForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user 
            address.save()
            print("jajasdkajsdkajsdkajskdjaskdj")
        else:
            print(form.errors)
        return redirect('accounts:profile')
    

def update_password(request):    
    print("get")
    if request.method == 'POST':
        print("booom")
        try:
            user = request.user
            user = User_Accounts.objects.get(id = user.id)
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
    return render(request , 'accounts/changepass.html')



def my_profile(request):
    current_user = request.user
    profile = Profile.objects.get(user=request.user)
    user = User_Accounts.objects.get(username = current_user.username)
    
    return render(request , 'accounts/myprofile.html',{'profile':profile,'user':user})


@transaction.atomic
def editprofile(request):
    if request.method == 'POST':
        user = request.user
        try:
            profile=Profile.objects.get(user = user)
        except Profile.DoesNotExist as e :
            profile = Profile(user = user)
        profile.first_name = request.POST.get('first_name')
        profile.last_name = request.POST.get('last_name')
        profile.date_of_birth = request.POST.get('birthday')
        profile.gender = request.POST.get('gender')
        profile.save()
        return redirect('accounts:profile')
    try:
        profile=Profile.objects.get(user = request.user)
        return render(request , 'accounts/editprofile.html',{'profile':profile})
    except Profile.DoesNotExist as e :
        return render(request , 'accounts/editprofile.html')
    
def addressbook(request):
    address = AddressBook.objects.filter(user = request.user)
    context = {
        'address' : address
        
    }
    
    return render(request , 'accounts/addressbook.html',context)    

def updateaddress(request):
    country = Country.objects.all()
    states = State.objects.all()
    addressform = AddressBookForm()
    context = {
        'states' : states,
        'country' : country,
        'addressform' : addressform, 
  
    }
    return render(request , 'accounts/addaddress.html',context)

def myorders(request):
    orders = Order.objects.filter(user = request.user).exclude(status="New").order_by('-created_at')
    context = {
        'orders':orders
    }
    
    return render(request , 'accounts/myorders.html',context)

def manage_order(request,id):
    order = Order.objects.get(id = id)
    products = OrderProduct.objects.filter(order = order)
    context = {
        'order' : order,
        'products' : products
    }
    return render(request , 'accounts/manageorder.html',context)


def returnedorders(request):
    orders = Order.objects.filter(user = request.user).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request , 'accounts/returnedorders.html')



    
    
    
    

  

