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
    path('order-success',views.order_success,name = 'order_success'),
     path('download_invoice/<str:order_id>/', views.download_invoice, name='download_invoice'),
    
    
    path('cancelorder',views.cancelorder, name='cancelorder'),
    path('returnorder',views.returnorder, name='returnorder'),
    path('cancelreturn',views.cancelreturn, name='cancelreturn'),

]

