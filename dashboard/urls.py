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
    path('product_item/<int:product_item_id>/', views.update_product_item, name='update_product_item'),
    path('changestatus/<int:id>/', views.changestatus, name='changestatus'),
    path('change_user_status/<str:name>/', views.change_user_status, name='change_user_status'),
    path('change_order_status/<int:id>/', views.change_order_status, name='change_order_status'),
    path('coupons', views.coupons, name='coupons'),
    path('add_coupons', views.add_coupons, name='add_coupons'),
    path('activate_coupon/<int:id>/', views.activate_coupon, name='activate_coupon'),
    path('disable_coupon/<int:id>/', views.disable_coupon, name='disable_coupon'),
    path('sales-report-pdf/', views.SalesReportPDFView.as_view(), name='sales_report_pdf'),
    
    path('carosal', views.carosal, name='carosal'),
    path('cursol_stat/<int:cid>/', views.cursol_stat, name='cursol_stat'),
    
    path('sales/', views.sales,name= 'sale'),
    path('sales_status/<int:id>/', views.sales_status,name= 'sales_status'),
    path('sales_delete/<int:id>/', views.sales_delete,name= 'sales_delete'),
    path('sales_edit/<int:id>/', views.sales_edit,name= 'sales_edit'),
    path('add_sale', views.add_sale,name= 'add_sale'),
]
