from django.contrib import admin
from django.urls import path, include, re_path
from . import views
app_name = 'accounts'

urlpatterns = [

    path('signup',views.signup, name='signup'),
    path('signin',views.signin, name='signin'),
    path('signinwithotp',views.signinotp, name='signinotp'),
    path('confirmlogin',views.otp, name='otp'),
    path('verifyemail',views.verifyemail, name='verifyemail'),
    path('profile',views.profile, name='profile'),
    path('profile/add_address',views.add_address, name='add_address'),
    path('profile/edit_address/<int:id>',views.edit_address, name='edit_address'),
    path('profile/delete_address/<int:id>',views.delete_address, name='delete_address'),
]
