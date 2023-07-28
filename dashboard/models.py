from django.db import models
import random
import string
from accounts.models import User_Accounts

# Create your models here.



def generate_coupon_code():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=10))

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, null=True)
    discount = models.PositiveIntegerField(null=True)
    max_discount = models.PositiveIntegerField(null=True)
    min_amount = models.IntegerField()
    active = models.BooleanField(default=True)
    uses = models.IntegerField(default=1)
    active_date = models.DateField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_coupon_code()
        super(Coupon, self).save(*args, **kwargs)

class Verify_coupon(models.Model):
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User_Accounts, on_delete=models.CASCADE,null=True)
    uses = models.PositiveIntegerField(default=0)