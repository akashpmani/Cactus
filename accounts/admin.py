from django.contrib import admin

# Register your models here.

from .models import User_Accounts,Cart,CartItem,AddressBook,Profile,State,Country

admin.site.register(User_Accounts)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(AddressBook)
admin.site.register(State)
admin.site.register(Country)