import datetime
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
import razorpay
from django.conf import settings
from store.views import cart_items2
from accounts.models import User_Accounts,Profile
from orders.models import AddressBook,CartItem,Order,OrderProduct,Payment
from accounts.models import CartItem,Cart
from products.models import Product_item,Products_Table

from django.template.loader import render_to_string
from django.core.mail import EmailMessage,send_mail
from django.conf import settings
# Create your views here.


def payment_details(request):
    current_user = request.user
    info = cart_items2(request)
    total_price = info['total']
    tax = info['tax']
    user = User_Accounts.objects.get(username=request.user.username)
    address_id = request.session['address_id']
    address = AddressBook.objects.get(id = address_id)
    data = Order()
    data.user = current_user
    data.address = address
    data.order_total = total_price
    data.tax = tax
    data.ip = request.META.get('REMOTE_ADDR')
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr,mt,dt)
    data.save()   
    current_date = d.strftime("%Y%m%d")
    data.order_number = current_date + str(data.id)
    data.save()    
    print(data.order_number)    
    return JsonResponse({'total' : total_price,'name' : user.username , 'email':user.email,'phone' : user.phone , 'order_number' :data.order_number })

def payment(request):
    print("ggg")
    order = Order.objects.get(user= request.user, is_ordered = False , order_number = request.POST.get('order_id'))
    payment = Payment(
        user= request.user,
        payment_id =request.POST.get('payment_id'),
        payment_method = request.POST.get('payment_mode'),
        amount_paid = order.order_total,
        status = request.POST.get('status'),
    )
    print("ggg")
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order = order
        orderproduct.payment = payment
        orderproduct.user = request.user
        orderproduct.product = item.product
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        print("ggg")

        # reduce quantity in stock
        product = Product_item.objects.get(id = item.product.id) 
        product.quantity -= item.quantity-1
        product.save()
        
        # clear cart
    CartItem.objects.filter(user=request.user).delete()
    
    # order confirmation email
    # mail_subject = 'Thank you for your Order!'
    # message = render_to_string( 'products/order_success_email.html', {
    #     'user': request.user,
    #     'order':order,
    #     })
    # to_email = request.user.email
    # send_email = EmailMessage(mail_subject,message,to=[to_email])
    # send_email.send()

    data ={
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


    
def order_complete(request):
    order_number = request.POST.get('order_number')
    transID = request.POST.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered= True)
        order.status = 'Confirmed'
        ordered_product = OrderProduct.objects.filter(order_id= order.id)
        subtotal =0
        for item in ordered_product:
            subtotal += item.product_price*item.quantity
        
        payment = Payment.objects.get(payment_id=transID)
        order.save()
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal
        }
        return render(request, 'products/ordersuccessfull.html',context)      
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('store:home')

def order_success(request):
    o_id = request.GET.get('order_number')
    t_id = payment_id = request.GET.get('payment_id')
    print("oid")
    print(o_id)
    print("tid")
    print(t_id)
    try:
        order = Order.objects.get(order_number=o_id, is_ordered= True)
        order.status = 'Confirmed'
        ordered_product = OrderProduct.objects.filter(order_id= order.id)
        subtotal =0
        for item in ordered_product:
            subtotal += item.product_price*item.quantity
        
        payment = Payment.objects.get(payment_id=t_id)
        order.save()
        address = AddressBook.objects.get(id = order.address.id)
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
            'address' : address,
        }
        try:
            profile = Profile.objects.get(user = request.user)
            context['profile'] = profile
        except:
            pass
        
        return render(request, 'products/ordersuccessfull.html',context) 
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('store:home')
    
      
def check_coupon(request):
    
    return JsonResponse({
        'code': 'order',
    })
    
    

def samp(request):
    return render(request, 'products/ordersuccessfull.html')


#  $.ajax({
#                   method: "POST",
#                   url: "/payment/order_complete",
#                   data: orderData,
#                   success: function(response) {
#                     console.log("Order complete response:", response);
#                     // Handle the response or perform any actions
#                   },
#                   error: function(xhr, status, error) {
#                     console.error("Order complete error:", error);
#                     // Handle the error case here
#                   }
#                 });