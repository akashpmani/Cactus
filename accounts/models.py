from datetime import timedelta, timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import AccountsManager
from products.models import Product_item

class User_Accounts(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    phone =  models.CharField(max_length=20, unique=True, blank=False)
    is_verified = models.BooleanField(default=False , blank=False )
    account_status = models.CharField(max_length=10, default='active', blank=True)
    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'username']
    suspension_end_date = models.DateTimeField(null=True, blank=True)
    objects = AccountsManager()   

    def suspend(self, days=1):
        self.is_active = False
        self.suspension_end_date = timezone.now() + timedelta(days=days)
        self.save()

    def is_suspended(self):
        return not self.is_active and self.suspension_end_date > timezone.now()

    def unsuspend(self):
        self.is_active = True
        self.suspension_end_date = None
        self.save()
    

    def __str__(self): 
        return self.username
    
def upload_path(instance, filename):
    # Get the username of the associated user
    username = instance.user.username

    # Construct the upload path
    upload_path = f'accounts/{username}/{filename}' 
    return upload_path


class Profile(models.Model):
    user = models.OneToOneField(User_Accounts, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to=upload_path)



class Cart(models.Model):
    cart_id = models.CharField(max_length=200, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self) :
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(User_Accounts, on_delete=models.CASCADE,null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE , related_name='cart_items' , null=True)
    product = models.ForeignKey(Product_item ,on_delete=models.SET_NULL , null=True , blank=True)
    quantity = models.PositiveIntegerField(null= False , blank=False)
    
    def sub_total(self):
        return self.product.price * self.quantity
    
    def __unicode__(self):
        return self.product
    
class AddressBook(models.Model):
    user = models.ForeignKey(User_Accounts,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10,null=True)
    default = models.BooleanField(default=False)
    
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    
class Country(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class State(models.Model):
    State = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name
    
 

