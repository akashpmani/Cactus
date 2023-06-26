from rest_framework import serializers
from products.models import Product_item

class Product_itemSerializer(serializers.Serializer):
    class meta:
        model = Product_item
        fields = ('product', 'size', 'price', 'quantity', 'created_at', 'is_active', 'slug', 'image')
    
    