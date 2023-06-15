from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import User_Accounts


class AccountSuspensionMiddleware:
    """a middleware for automattically handle the suspended accounts and turns back to 
       active if the suspension period is over
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        #gets all suspended accounts
        suspended_accounts = User_Accounts.objects.filter(account_status='suspended')
        

        # for checking account should be unsuspended or not
        for account in suspended_accounts:
            if account.suspension_end_date <= timezone.now():
                print(account)
                account.account_status = 'active'
                account.save()

        return response
