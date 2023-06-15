from django.contrib import admin
from django.urls import path, include, re_path
from . import views
app_name = 'store'

urlpatterns = [

    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('allproducts/', views.allproducts, name='allproducts'),
    path('product/<str:category>/<str:slug>/<int:id>/', views.product_detail, name='product_detail'),
    # path('<slug:category_slug>',views.shop,name ="product_by_category"),
    path('tag/<str:tag_name>',views.product_by_tags,name ="product_by_tags"),
    path('featured/<int:id>',views.classifiedproducts, name ="classifiedproducts"),
    path('profile',views.profile,name='profile'),
    path('cart/',views.cart,name="cart"),
    path('add_cart/<int:product_id>/<int:quantity>/',views.add_cart,name="add_cart"),
    path('remove_cart/<int:product_id>',views.remove_cart,name="remove_cart"),
    path('delete_cart/<int:product_id>',views.delete_cart,name="delete_cart"),
    path('checkout_manager/', views.checkout_manager, name='checkout_manager'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
      

]
