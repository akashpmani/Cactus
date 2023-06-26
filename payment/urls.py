from django.contrib import admin
from django.urls import path, include, re_path
from . import views
app_name = 'payment'

urlpatterns = [

    path('pay-with-razor',views.pay_with_razorpay, name='pay_with_razorpay'),
    path('payment',views.payment, name='payment'),

]

