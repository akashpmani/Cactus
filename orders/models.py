from datetime import timedelta, timezone
from django.db import models
from accounts.models import AddressBook,CartItem,Profile,User_Accounts
from products.models import Product_item,Products_Table

# Create your models here.
class Payment(models.Model):
    user        = models.ForeignKey(User_Accounts, on_delete=models.CASCADE)
    payment_id  = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    amount_paid = models.CharField(max_length=50)
    status      = models.CharField(max_length=100)
    created_at  = models.DateTimeField(auto_now_add=True)
    spike_use = models.BooleanField(default=False)
    spike_discount = models.PositiveBigIntegerField(default = 0)
    coupon_use = models.BooleanField(default = False)
    coupon_discount = models.PositiveIntegerField(default=0)
    coupon_code = models.CharField(max_length=50,default='')
     
    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    STATUS = (
        ('New','New'),
        ('Confirmed','Confirmed'),
        ('shipping','shipping'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
        ('Return initiated','Return initiated'),
        ('Returned','Returned'),
    )
    
    user    = models.ForeignKey(User_Accounts, on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL , blank=True, null= True) 
    order_number = models.CharField(max_length=50)
    address = models.ForeignKey(AddressBook,on_delete=models.SET_NULL,unique=False, null= True ,blank=True,)
    order_note = models.CharField(max_length=50, blank=True)
    order_total = models.FloatField( )
    tax = models.FloatField( )
    status = models.CharField(max_length=50,choices=STATUS,default='New')
    ip = models.CharField(max_length=50,blank=True)
    is_ordered = models.BooleanField(default= False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deliverd_at = models.DateTimeField(null=True)
    returned_at = models.DateTimeField(null=True)
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    def __str__(self):
        return self.first_name
    def can_return_products(self):
        if self.delivered_at:
            current_date = timezone.now()
            return self.delivered_at + timedelta(days=3) >= current_date
        return False
    
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL,blank=True, null=True)
    user = models.ForeignKey(User_Accounts, on_delete=models.CASCADE)
    product = models.ForeignKey(Product_item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product.product_name
    
