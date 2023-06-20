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
    path('profile/update_password/<int:id>',views.update_password, name='update_password'),
]
class Solution:
    def secondHighest(self, s: str) -> int:
        lar =-1
        sec_lar =-1
        
        for i in s:
            if i.isdigit():
                sec_lar = lar
                lar = int(i)
            if i.isdigit():
                if int(i) < lar and int(i) > sec_lar and int(i) != lar:
                    sec_lar = int(i)
        return sec_lar
                 
