from datetime import timedelta
from django.utils import timezone
from django.utils import timezone
from celery import shared_task
from .models import User_Accounts

# @shared_task()
# def delete_expired_otp(user_id):
#     print("hrlloof")
#     user = User_Accounts.objects.get(id=user_id)
#     if not user.is_verified:
#         user.otp = None
#         user.save()



class Message_Handler:
    phone_number = None
    otp = None
    
    def __init__(self,numb,otp) -> None:
        self.phone_number = numb
        self.otp = otp
    
    def send_otp(self):
        pass
        
    
    