import json
from django.http import JsonResponse
from django.shortcuts import render
import razorpay
from django.conf import settings
from store.views import cart_items2
from accounts.models import User_Accounts
from orders.models import AddressBook,CartItem,Order,OrderProduct,Payment
from accounts.models import CartItem,Cart
from products.models import Product_item,Products_Table

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
# Create your views here.


def pay_with_razorpay(request):
    info = cart_items2(request)
    total_price = info['total']
    # Client = razorpay.Client(auth = (settings.razor_pay_key_id , settings.key_secret))
    # payment = Client.order.create({'ammount' : info.tax.total_price , 'currency' : 'INR','payment_capture' : 1,})
    user = User_Accounts.objects.get(username=request.user.username)
    context ={ 
            #   'payment' : payment ,
            'total' : total_price ,
    }
    context.update(cart_items2(request))
    return JsonResponse({'total' : total_price,'name' : user.username , 'email':user.email,'phone' : user.phone})



def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user= request.user, is_ordered = False , order_number = body['orderID'])
    payment = Payment(
        user= request.user,
        payment_id =body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
        
        # reduce quantity in stocsk
        product = Product_item.objects.get(id=item.product_id) 
        product.stock -= item.quantity
        product.save()
        
        # clear cart
    CartItem.objects.filter(user=request.user).delete()
    
    # order confirmation email
    mail_subject = 'Thank you for your Order!'
    message = render_to_string( 'joejee/order_recieved_email.html', {
        'user': request.user,
        'order':order,
        })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()
                   
    # send response back via Json
    data ={
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)
