from django.contrib import admin

# Register your models here.
from .models import Products_Table, Category, Product_item, Product_Tags, Product_Color,P_tags,ProductClassification,classfiedProducts
from .models import *

admin.site.register(Products_Table)
admin.site.register(Product_item)
admin.site.register(Product_images)
admin.site.register(Product_Tags)
admin.site.register(Product_Color)
admin.site.register(Category)
admin.site.register(P_tags)
admin.site.register(ProductClassification)
admin.site.register(classfiedProducts)
