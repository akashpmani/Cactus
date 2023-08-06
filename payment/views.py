import datetime
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
import razorpay
from django.conf import settings
from store.views import cart_items2
from accounts.models import User_Accounts,Profile,Wallet
from orders.models import AddressBook,CartItem,Order,OrderProduct,Payment
from accounts.models import CartItem,Cart,Wallet,Transaction
from products.models import Product_item,Products_Table

from django.template.loader import render_to_string
from django.core.mail import EmailMessage,send_mail
from django.conf import settings
from dashboard.models import Coupon,Verify_coupon
from django.http import HttpResponse
from django.template.loader import get_template
from .helpers import save_pdf
# Create your views here.


def payment_details(request):
    current_user = request.user
    info = cart_items2(request)
    total_price = info['total']
    tax = info['tax']
    user = User_Accounts.objects.get(username=request.user.username)
    address_id = request.session['address_id']
    address = AddressBook.objects.get(id = address_id)
    wallet = request.GET.get('wallet')
    print(type(wallet))
    coupon_code = request.GET.get('code')
    spike_use = False
    spike_discount = 0
    coupon_use = False
    coupon_discount = 0
    
    
    if coupon_code == 'true':
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                coupon_discount = min((total_price/100)*coupon.discount,coupon.max_discount)
                print(coupon_discount)
                total_price = total_price - coupon_discount
                coupon_use = True
                coupon_code = coupon_code
            except Coupon.DoesNotExist:
                pass
    if wallet == 'true':
        wal = Wallet.objects.get(user = request.user)
        total_price -= wal.balance
        spike_use = True
        spike_discount = wal.balance
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
    return JsonResponse({'total' : total_price,'name' : user.username , 'email':user.email,
                         'phone' : user.phone , 'order_number' :data.order_number,'coupon_discount':coupon_discount,
                        'coupon_use':coupon_use,'coupon_code' : coupon_code,'spike_use':spike_use,'spike_discount':spike_discount })

def payment(request):
    order = Order.objects.get(user= request.user, is_ordered = False , order_number = request.POST.get('order_id'))
    if request.POST.get('spike_use') == 'true':
        spiked = True
        wal = Wallet.objects.get(user = request.user)
        Transaction.objects.create(user = request.user , amount = wal.balance , transaction_type = 'debit' ,
                        description = 'Payed using spike order ref number'+str(order.order_number))
        wal.balance = 0
        wal.save()
    else:
        spiked  = False
    if request.POST.get('coupon_use') == 'true':
        coped = True
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code)

            try:
                verify_use = Verify_coupon.objects.get(user=request.user, coupon=coupon)
                verify_use.uses += 1
            except:
                verify_use = Verify_coupon.objects.create(user=request.user, coupon=coupon, uses=1)
            verify_use.save()
        except Coupon.DoesNotExist:
            # Handle the case when the Coupon with the provided code does not exist
            # You can show an error message to the user or perform any other appropriate action
            print("Coupon with code", coupon_code, "does not exist")
    else:
        coped = False

   
    payment = Payment(
        user= request.user,
        payment_id =request.POST.get('payment_id'),
        payment_method = request.POST.get('payment_mode'),
        amount_paid = order.order_total,
        status = request.POST.get('status'),
        spike_use = spiked ,
        spike_discount = request.POST.get('spike_discount'),
        coupon_use = coped,
        coupon_discount = request.POST.get('coupon_discount'),
        coupon_code = request.POST.get('coupon_code'),
     
    )
    
    payment.save()
    print(payment)
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
        discount = ( subtotal * .2 ) - order.order_total 
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
            'discount' : discount
        }
        return render(request, 'products/ordersuccessfull.html',context)      
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('store:home')

def order_success(request):
    o_id = request.GET.get('order_number')
    t_id = payment_id = request.GET.get('payment_id')
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


def cancelorder(request):
    order_id = request.GET.get('order_id')

    order = Order.objects.get(id = order_id)
    spike = order.payment.spike_use
    if order.payment.payment_method =="cod":
        if spike:
            discount = order.payment.spike_discount
            wallet = Wallet.objects.get(user = request.user)
            wallet.balance += discount
            wallet.save()
            if discount > 0:
                trans = Transaction.objects.create(user = request.user , amount = discount , transaction_type = 'credit' ,
                            description = 'Refund for cancelled order ref number'+str(order.order_number))
            trans.save()
    if order.payment.payment_method =="razorpay":
        total =  order.order_total
        total -= order.payment.coupon_discount
        wallet = Wallet.objects.get(user = request.user)
        wallet.balance += total
        print(total)
        print(total)
        print(wallet.balance)
        print(wallet.balance)
        wallet.save()
        Transaction.objects.create(user = request.user , amount = total , transaction_type = 'credit' , description = 'Refund for Cancelled order')

    order.status = 'Cancelled'
    order.save()
    response_data = {'canceled': 'Order cancellation successful'}
    return JsonResponse(response_data)

def returnorder(request):
    order_id = request.GET.get('order_id')

    order = Order.objects.get(id = order_id)
    order.status = 'Return initiated'
    order.save()
    response_data = {'return': 'Order return initiated successfully , Our pickup team will be at the deliverd address shortly '}
    return JsonResponse(response_data)

def cancelreturn(request):
    order_id = request.GET.get('order_id')

    order = Order.objects.get(id = order_id)
    order.status = 'Delivered'
    order.save()
    response_data = {'return': 'Order return Canceled successfully '}
    return JsonResponse(response_data)
    
    
    
from django.http import HttpResponse
from .helpers import save_pdf

def download_invoice(request,order_id):
    try:
        order = Order.objects.get(order_number=order_id, is_ordered= True)
        order.status = 'Confirmed'
        ordered_product = OrderProduct.objects.filter(order_id= order.id)
        subtotal =0
        for item in ordered_product:
            subtotal += item.product_price*item.quantity
        payment = Payment.objects.get(payment_id=order.payment)
        order.save()
        address = AddressBook.objects.get(id = order.address.id)
        params = {
            
            'order':order,
            'ordered_product':ordered_product,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
            'address' : address,
        }
        file_name, success = save_pdf(params)
        
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('store:home')
        
    if success:
        response = HttpResponse(file_name, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        return response
    else:
        # Handle error case here, like displaying an error message to the user.
        return HttpResponse("Failed to generate the invoice.", status=500)
