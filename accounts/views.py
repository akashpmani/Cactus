from datetime import timedelta, timezone
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .models import User_Accounts,AddressBook,Profile,Country,Cart,State,Wallet,Transaction,CartItem
from . forms import CustomerRegisterForm, Signin_Form , Otp_Form ,AddressBookForm
from django.contrib.auth import get_user_model
from django.contrib import messages,auth
from .manager import AccountsManager
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.utils import timezone
import random
from django.contrib.auth import login as auth_login
from . import verify
from .otp import verify_otp
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from orders.models import Order,OrderProduct,Payment
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
from store.views import _cart_id
# from .helpers import delete_expired_otp
# Create your views here.

account_manager = AccountsManager()

def signup(request):
    if request.method == 'POST':
        signupform = CustomerRegisterForm(request.POST)
        if signupform.is_valid():
            user = signupform.save()
            wallet = Wallet.objects.create(user=user, balance=100)
            Transaction.objects.create(user=user, amount=100, transaction_type='credit', description='Signup bonus')

            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_items = CartItem.objects.filter(cart=cart)
                    for item in cart_items:
                        item.user = user
                        item.cart = None
                        item.save()
            except Cart.DoesNotExist:
                pass
        else:
            for field_name, errors in signupform.errors.items():
                for error in errors:
                    messages.error(request, f"{field_name}: {error}")
            return redirect('accounts:signup')

    form = CustomerRegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        loginform = Signin_Form(request.POST)
        if loginform.is_valid():
            login_cred = loginform.cleaned_data['login_cred']
            password = loginform.cleaned_data['password']
            user = account_manager.authenticate(request, email=login_cred, phone=login_cred, username=login_cred, password=password)

            if user is not None:
                auth_login(request, user)

                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()

                    if is_cart_item_exist:
                        cart_items = CartItem.objects.filter(cart=cart)

                        for item in cart_items:
                            item_in_user_cart = CartItem.objects.filter(user=user, product=item.product).exists()

                            if item_in_user_cart:
                                product = CartItem.objects.get(user=user, product=item.product)
                                product.quantity = item.quantity
                                item.delete()
                                product.save()
                            else:
                                new_cart_item = CartItem(user=user, quantity=item.quantity, product=item.product)
                                new_cart_item.save()
                except Cart.DoesNotExist:
                    pass

                return redirect("store:home")
            else:
                messages.error(request, 'Invalid login credentials')
                return render(request, 'accounts/signin.html', {'form': loginform})
        else:
            # Form is not valid; display form errors
            for field_name, errors in loginform.errors.items():
                for error in errors:
                    messages.error(request, f"{field_name}: {error}")
            return render(request, 'accounts/signin.html', {'form': loginform})
    else:
        loginform = Signin_Form()

    return render(request, 'accounts/signin.html', {'form': loginform})

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
                try:
                    cart = Cart.objects.get(cart_id= _cart_id(request))
                    is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                    if is_cart_item_exist:
                        cart_items = CartItem.objects.filter(cart=cart)
                        for item in cart_items:
                            item_in_user_cart = CartItem.objects.filter(user = user,product = item.product).exists()
                            if item_in_user_cart:
                                product = CartItem.objects.get(user = user,product = item.product)
                                product.quantity = item.quantity
                                item.delete()
                                product.save()
                            else:
                                new_cart_item = CartItem(user=user, quantity=item.quantity, product=item.product)
                                new_cart_item.save()
                except:
                    pass
                return redirect("store:home")
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


def log_out(request):
    logout(request)
    return redirect('store:home')
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
                d_address = AddressBook.objects.get(user = user ,default = True)
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
    user = User_Accounts.objects.get(username = current_user.username)
    context = {
        'user':user
        }
    try:
        if Profile.objects.filter(user = user).exists:
            profile = Profile.objects.get(user = user)
            context['profile'] = profile
    except:
        pass
    return render(request , 'accounts/myprofile.html',context)


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
    if request.method == 'POST':
        status = request.POST.get('status')
        print(status)
        if status:
            orders = Order.objects.filter(user=request.user, status=status).exclude(status="New").order_by('-created_at')
        else:
            orders = Order.objects.filter(user=request.user).exclude(status="New").order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).exclude(status="New").order_by('-created_at')
    
    context = {
        'orders':orders
    }
    
    return render(request , 'accounts/myorders.html',context)
from django.shortcuts import get_object_or_404

def manage_order(request, id):
    order = None
    try:
        order = get_object_or_404(Order, id=id)
        products = OrderProduct.objects.filter(order=order)
        address = AddressBook.objects.get(id=order.address.id)
        return_status = False
        if order.status == "Delivered":
            current_date = timezone.now()
            return_status = order.deliverd_at + timedelta(days=3) >= current_date
        print(return_status)
    except Order.DoesNotExist:
        return redirect('accounts:profile')
    context = {
        'order': order,
        'products': products,
        'address': address,
        'net': order.order_total - order.tax if order else 0,
        'return_status': return_status
    }
    return render(request, 'accounts/manageorder.html', context)


def returnedorders(request):
    orders = Order.objects.filter(user = request.user).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request , 'accounts/returnedorders.html')



def wallet(request):
    try:
        wallet = Wallet.objects.get(user = request.user)
        
    except ObjectDoesNotExist:
        wallet = Wallet.objects.create(user=request.user, balance=100)
        Transaction.objects.create(user=request.user,amount=100,transaction_type='credit',description='Signup bonus',)
    transaction = Transaction.objects.filter(user = request.user).order_by('-id')
    context = {
        'wallet' : wallet,
        'transaction' : transaction
    }  
    return render(request , 'accounts/wallet.html',context) 
    
    
def forgotpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if User_Accounts.objects.filter(email=email).exists():
            user = User_Accounts.objects.get(email__exact=email)

            current_site = get_current_site(request)
            subject = 'Cactus : Reset your password'
            body = render_to_string('accounts/resetmailcontant.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, body, to=[to_email])
            send_email.send()
            messages.success(
                request, 'Password reset email has been sent to your email address')
            return render(request,'accounts/linksendsuccess.html')
        else:
            messages.error(request, "Account Does't Exists!!!")
            return redirect('accounts:forgotpassword')
    return render(request,'accounts/resetpasswordpage.html')
    
def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User_Accounts._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User_Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.!')
        return redirect('accounts:resetpassword')
    else:
        messages.error(request, 'Sorry, the activation link has expired.!')
        return redirect('accounts:signin')


def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['Confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = User_Accounts.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "sucessfully reset password")
            return render(request,'accounts/resetsuccess.html')

        else:
            messages.error(request, "Passwords are not match")
            return redirect('accounts:resetpassword')
    else:
        return render(request, 'accounts/resetpassmail.html')


    

  



