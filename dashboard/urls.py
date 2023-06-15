from django.contrib import admin
from django.urls import path, include, re_path
from . import views
app_name = 'dashboard'

urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('usermanager/', views.usermanager, name='usermanager'),
    path('pro', views.products, name='products'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('orders/', views.orders, name='orders'),
    path('addcategory/', views.addcategory, name='addcategory'),
    path('addtags/', views.addtags, name='addtags'),
    path('addnewproduct/', views.addnewproduct, name='addnewproduct'),
    path('addproductitems/', views.addproductitems, name='addproductitems'),
    path('editcategory/<int:category_id>/', views.edit_category, name='edit_category'),
    path('deletecategory/<int:category_id>/', views.delete_category, name='deletecategory'),
    path('edittags/<int:tag_id>/', views.edit_tags, name='edit_tags'),
    path('deletetags/<int:tag_id>/', views.delete_tags, name='deletetags'),
    path('deleteproduct/<int:id>/', views.delete_product, name='deleteproduct'),
    path('productstatus/<int:id>/', views.status, name='productstatus'),
    path('productlist', views.pro, name='pro'),    
    path('productdetails/<int:id>/', views.productdetails, name='productdetails'),     
    path('deleteimage/<int:id>/<int:image_id>/', views.deleteimage, name='deleteimage'),    
    path('upload_image/<int:id>/', views.upload_image, name='upload_image'), 
    path('changethumbnail/<int:id>/', views.changethumbnail, name='changethumbnail'),
    path('users', views.users, name='users'),
    path('userdetails/<int:id>/', views.userdetails, name='userdetails'),
    # path('pro', views.products, name='products'),
]
