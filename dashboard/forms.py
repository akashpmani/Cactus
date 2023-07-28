from django import forms
from . models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model=Coupon
        fields = ['discount','code' ,'max_discount', 'min_amount', 'active','uses' ,  'active_date', 'expiry_date']
        widgets = {
            'discount': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'min_amount': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'active_date': forms.DateInput(attrs={'class': 'form-control datepicker mb-3'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control datepicker mb-3'})
        }