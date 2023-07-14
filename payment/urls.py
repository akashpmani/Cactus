from django.contrib import admin
from django.urls import path, include, re_path
from . import views
app_name = 'payment'

urlpatterns = [

    path('payment_details',views.payment_details, name='payment_details'),
    path('payment',views.payment, name='payment'),
    path('check_coupon',views.check_coupon, name='check_coupon'),
    path('samp',views.samp, name='samp'),
    path('order_complete',views.order_complete, name='order_complete'),

]

