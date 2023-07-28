from django.contrib import admin
from django.urls import path, include, re_path
from . import views
app_name = 'accounts'
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('signup',views.signup, name='signup'),
    path('signin',views.signin, name='signin'),
    path('signinwithotp',views.signinotp, name='signinotp'),
    path('confirmlogin',views.otp, name='otp'),
    path('logout',views.log_out, name='logout'),
    path('forgotpassword',views.forgotpassword, name='forgotpassword'),
    
    path('verifyemail',views.verifyemail, name='verifyemail'),
    path('profile',views.profile, name='profile'),
    path('profile/add_address',views.add_address, name='add_address'),
    path('profile/edit_address/<int:id>',views.edit_address, name='edit_address'),
    path('profile/delete_address/<int:id>',views.delete_address, name='delete_address'),
    path('profile/update_password',views.update_password, name='update_password'),
    path('myprofile',views.my_profile, name='my_profile'),
    path('editprofile',views.editprofile, name='editprofile'),
    path('addressbook',views.addressbook, name='addressbook'),
    path('updateaddress',views.updateaddress, name='updateaddress'),
    path('myorders',views.myorders, name='myorders'),
    path('manage_order/<int:id>',views.manage_order, name='manage_order'),
    path('returnedorders',views.returnedorders, name='returnedorders'),
    path('wallet',views.wallet,name="mywallet"),
    
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('reset_password/<uidb64>/<token>/',views.reset_password,name='reset_password'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
]

