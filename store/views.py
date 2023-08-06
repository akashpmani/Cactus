import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import AddressBook,Country, State
from products.models import Category, Product_Tags, Products_Table, Product_item, Product_images,P_tags,ProductClassification,classfiedProducts
from accounts.models import Cart, CartItem ,Wallet ,Transaction
from accounts.forms import AddressBookForm,CustomerRegisterForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core import serializers
from .serilizers import Product_itemSerializer
from rest_framework.renderers import JSONRenderer
import json
from django.core.serializers.json import DjangoJSONEncoder
from accounts.forms import CustomerRegisterForm, Signin_Form , Otp_Form ,AddressBookForm
from django.contrib.auth import get_user_model
from django.contrib import messages,auth
from accounts.manager import AccountsManager
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from accounts import verify
from django.db.models import Q
from dashboard.models import Verify_coupon,Coupon,CarouselItem
import random
from django.db.models import F
# Create your views here.
account_manager = AccountsManager()

def search_view(request):
    query = request.GET.get('q', '')
    results = Products_Table.objects.filter(name__icontains=query)[:5]
    search_results = [{'name': product.name, 'image': product.image.url, 'slug': product.slug} for product in results]
    return JsonResponse(search_results, safe=False)


import random

def home(request):
    current_user = request.user
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    classification = ProductClassification.objects.all()
    carosal = CarouselItem.objects.filter(active = True)
    random_products = Product_item.objects.filter(offer_price__lt=F('price'), is_active=True).order_by('?')[:4]
    
    context = {
        'categories': categories,
        'tags': tags,
        'classification': classification,
        'random_products': random_products,
        'carosal':carosal,
    }
    
    context.update(cart_items(request))
    return render(request, 'products/index.html', context)


def products(request):
    try:
        searchContent = request.GET.get('searchContent','')  
    except:
        pass
    print(searchContent)
    matching_tags = Product_Tags.objects.filter(tag_name__icontains=searchContent)
    matching_product_ids = P_tags.objects.filter(tag__in=matching_tags).values_list('product__id', flat=True)
    product_items = Product_item.objects.filter(
        Q(product__name__icontains=searchContent) | 
        Q(product__description__icontains=searchContent) | 
        Q(product__category__category_name__icontains=searchContent) |
        Q(product__id__in=matching_product_ids) 
        ).order_by('id')
    if request.method == 'POST':
        print("reached")
        filter_data = json.loads(request.body)
        min_price = float(filter_data.get('minPrice'))
        max_price = float(filter_data.get('maxPrice'))*5
        categories = filter_data.get('categories')
        sizes = list(filter_data.get('sizes'))
        tags = filter_data.get('tags')
        searchContent = filter_data.get('searchContent')
        page = int(filter_data.get('page'))
        sort = int(filter_data.get('sort'))
        # Start with all products from the Product_Table
        
        # Filter based on selected tags
        if tags:
            queryset = Products_Table.objects.filter(p_tags_set__tag__tag_name__in=tags)
        else:
            queryset = Products_Table.objects.all()
        # Filter based on selected categories
        if categories:
            queryset = queryset.filter(category__category_name__in=categories)
        product_items = Product_item.objects.filter(product__in=queryset)
        #Filter based on selected sizes
        if sizes:
            print(sizes)
            product_items = product_items.filter(size__in=sizes)
        if searchContent != '':
            matching_tags = Product_Tags.objects.filter(tag_name__icontains=searchContent)
            matching_product_ids = P_tags.objects.filter(tag__in=matching_tags).values_list('product__id', flat=True)
        if min_price is not None and max_price is not None:
            product_items = product_items.filter(
                Q(product__name__icontains=searchContent) |
                Q(product__description__icontains=searchContent) |
                Q(product__category__category_name__icontains=searchContent) |
                Q(product__id__in=matching_product_ids),
                price__range=(min_price, max_price)
            )
        if sort:
            if sort == 0:
                pass
            elif sort == 1:
                product_items = product_items.filter().order_by('-price')
            elif sort == 2:
                product_items = product_items.filter().order_by('price')
            elif sort == 3:
                product_items = product_items.filter().order_by('product__name')
                
        paginator = Paginator(product_items, 12)
        product_items = paginator.get_page(page)
        total_pages = paginator.num_pages
        for i in product_items:
            print(i)
        filtered_items = [
        {
            'id': item.id,
            'name': item.product.name,
            'price' : item.price,
            'offer_price' : item.offer_price,
            'slug' : item.slug,
            'size' : item.size,
            'image' : item.image.url,
            
            
        }
        for item in product_items 
        ]
        return JsonResponse({'filtered_items': filtered_items,'searchContent':searchContent,'total_pages' : total_pages,'curr': page,})
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()   
    paginator = Paginator(product_items,12)
    page_number = 1
    if request.method == 'POST':
        page_number = request.POST.get('page')
    productFinal = paginator.get_page(page_number)
    total_pages = paginator.num_pages
    context = {
        'product': productFinal, 
        'categories': categories,
        'tags': tags,
        'total_pages': total_pages,
        'curr': page_number,
        'searchContent':searchContent
    }
    context.update(cart_items(request))
    return render(request, 'products/productlist.html', context)


def allproducts(request):

    product = Products_Table.objects.order_by('id')
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    paginator = Paginator(product,12)
    page_number = 1
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse the JSON data
        page_number = data.get('page')
        productFinal = paginator.get_page(page_number)
        serialized_product = serializers.serialize('python', productFinal)
        product_list = [item['fields'] for item in serialized_product]
        total_pages = paginator.num_pages
        context = {
            'product': product_list, 
            'categories': list(categories.values()),
            'tags': list(tags.values()),
            'total_pages': total_pages,
            'curr': page_number
        }
        context.update(cart_items(request))
        response_data = {
            "status": "products fetched",
            "context": context
        }
        return JsonResponse(response_data)

    productFinal = paginator.get_page(page_number)
    total_pages = paginator.num_pages
    context = {
        'product': productFinal, 
        'categories': categories,
        'tags': tags,
        'total_pages': total_pages,
        'curr': page_number
    }
    context.update(cart_items(request))
    return render(request,'products/productlist.html',context)

def product_by_tags(request, tag_name):
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    tag = Product_Tags.objects.get(tag_name=tag_name)
    p_t = tag.p_tags_set.all()
    products = []
    for o in p_t:
        products.append(o.product)
    items = []
    for product in products:
        items.extend(Product_item.objects.filter(product=product))
    # context = {
    #     'product': items,
    #     'categories': categories,
    #     'tags': tags,
    # }
    # context.update(cart_items(request))

    # return render(request, 'products/productlist.html', context)
    paginator = Paginator(items, 1)
    page_number = 1
    if request.method == 'POST':
        page_number = request.POST.get('page')
    productFinal = paginator.get_page(page_number)
    total_pages = paginator.num_pages
    context = {
        'product': productFinal, 
        'categories': categories,
        'tags': tags,
        'total_pages': total_pages,
        'curr': page_number
    }
    
    context.update(cart_items(request))
    return render(request, 'products/productlist.html', context)

def classifiedproducts(request,id):
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    classification = ProductClassification.objects.get(id = id)
    print(classification.title)
    class_products = classfiedProducts.objects.filter(classification=classification)
    product = []
    for p in class_products:
        product.append(p.product)
    items = []
    for pro in product:
        items.extend(Product_item.objects.filter(product=pro))
    context = {
        'product':items,
        'categories': categories,
        'tags': tags,
    }
    context.update(cart_items(request))

    return render(request, 'products/productlist.html', context)



def product_detail(request, slug , size):
    product = Products_Table.objects.get(slug=slug)
    cat = product.category
    print(cat)
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    var = Product_item.objects.get(product=product,size = size)
    varients = Product_item.objects.filter(product=product)
    images = Product_images.objects.filter(product=product)

    related_prod = Products_Table.objects.filter(category__category_name=cat)
    print(size)


    context = {
        'var':var,
        'size' : size,
        'data': product,
        'reldata': related_prod,
        'categories': categories,
        'tags': tags,
        'varients': varients,
        'images': images,
    }
    context.update(cart_items(request))

    return render(request, 'products/product.html', context)


def profile(request):

    return render(request, 'accounts/profile1.html')


def cart(request):
    current_user = request.user
    total = 0
    product_data = []
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart.id)
 
        for item in cart_items:
            if item.quantity > item.product.quantity:
                item.in_stock = False
                in_stock = False
            else:
                item.in_stock = True
                in_stock = True
            item.save()
            product_item = item.product
            id = product_item.id
            product_table = product_item.product
            size = product_item.size
            price = product_item.price
            total += price * item.quantity
            image = product_table.image
            quantity = item.quantity
            name = product_table.name

            product_dict = {
                'id' : id,
                'name': product_table.name,
                'description': product_table.description,
                'size': size,
                'price': price,
                'quantity': quantity,
                'total_price' : quantity*price,
                'name': name,
                'image': image,
                'in_stock' : in_stock
            }
            product_data.append(product_dict)
        tax_t = round(total * 0.2, 3)
        g_total = total + tax_t
        tax = {
            'cart_items' : cart_items,
            'net' : total,
            'total': g_total,
            'tax': tax_t,
        }
    except Cart.DoesNotExist:
        tax = {
            'cart_items' : None,
            'net' : None,
            'total': None,
            'tax': None,
        }

    context = {
        'product_data': product_data,
        'tax': tax,
    }
    context.update(catcom(request))
    return render(request,"products/cart.html",context)

def cart_items2(request, total=0, quantity=0, cart_items=None):

    current_user = request.user
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart)
        total_price = 0
        product_data = []
        products = []
        for item in cart_items:
            product_item = item.product
            products.append(product_item)
            product_table = product_item.product
            size = product_item.size
            price = product_item.price
            
            image = product_table.image
            quant = item.quantity
            total_price += price*quant
            name = product_table.name
            product_dict = {
                'item_id' : product_item,
                'name': product_table.name,
                'description': product_table.description,
                'size': size,
                'price': price,
                'quantity': quant,
                't_price' : quant*price,
                'name': name,
                'image': image,
            }
            product_data.append(product_dict)
        tax = round(total_price * 0.2, 3)
        total_price += tax
        total_price = round(total_price,3)
       
        context = {
        'cart_items' : products,
        'product_data': product_data,
        'tax': tax,
        'total': total_price,
        'tax': tax,
        }

        return context
    except Cart.DoesNotExist:
        pass
    product_data = []
    tax = {
        'total': total,
        'tax': 0,
    }
    context = {
        'product_data': product_data,
        'tax': tax,
    }
    context.update(catcom(request))
    return context


def cart_info(request):

    current_user = request.user
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart)
        net = 0
        for item in cart_items:
            quant = item.quantity
            price = item.product.price
            net += price*quant
        tax = round(net * 0.2, 3)
        total = tax +net
        context = {
        'net' : net,
        'total': total,
        'tax': tax,
        }
        
        return context
    except Cart.DoesNotExist:
        pass
    context = {
        'net' : 0,
        'total': 0,
        'tax': 0,
    }

    return context

def cart_items(request, total=0, quantity=0, cart_items=None):

    current_user = request.user
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart)
        total_price = 0
        product_data = []
        products = []
        for item in cart_items:
            product_item = item.product
            products.append(product_item)
            product_table = product_item.product
            size = product_item.size
            price = product_item.price
            total_price += price * item.quantity
            image = product_table.image
            quant = item.quantity
            name = product_table.name
            product_dict = {
                'item_id' : product_item,
                'name': product_table.name,
                'description': product_table.description,
                'size': size,
                'price': price,
                'quantity': quant,
                'total_price' : quant*price,
                'name': name,
                'image': image,
            }
            product_data.append(product_dict)
        tax = round(total_price * 0.2, 3)
        net = total_price
        total_price += tax
        tax = {
            'total': total_price,
            'tax': tax,
            'net' : net
        }
        context = {
        'cart_items' : products,
        'product_data': product_data,
        'tax': tax,
        }

        return context
    except Cart.DoesNotExist:
        pass
    product_data = []
    tax = {
        'total': total,
        'tax': 0,
    }
    context = {
        'product_data': product_data,
        'tax': tax,
    }

    return context


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id,quantity = None):
    print("hooi")
    current_user = request.user
    product = Product_item.objects.get(id=product_id)
    if current_user.is_authenticated:
        # try:
        #     cart = CartItem.objects.get(user = current_user)
        # except Cart.DoesNotExist:
        #     cart = CartItem.objects.create(user = current_user)   
        is_cart_item_exist = CartItem.objects.filter(
            user = current_user, product=product).exists()    
        if is_cart_item_exist:
            cart_item = CartItem.objects.get(user = current_user, product=product)
            if quantity:
                cart_item.quantity += quantity
            else:
                cart_item.quantity += 1
            cart_item.save()

        else:
            if quantity:
                cart_item = CartItem.objects.create(
                product=product, quantity=quantity,user = current_user,)
            else:
                cart_item = CartItem.objects.create(
                product=product, quantity=1,user = current_user,)
            cart_item.save()
        
    else:      
        if request.method == "POST":
            product = Product_item.objects.get(id=product_id)
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        is_cart_item_exist = CartItem.objects.filter(
            product=product, cart=cart).exists()
        if is_cart_item_exist:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            if quantity:
                cart_item.quantity +=  quantity
            else:
                cart_item.quantity += 1
            cart_item.save()
            
        else:
            if quantity:
                cart_item = CartItem.objects.create(
                product=product, quantity=quantity, cart= cart)
            else:
                cart_item = CartItem.objects.create(
                product=product, quantity=1, cart= cart)
            cart_item.save()
    referring_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(referring_page)


def remove_cart(request, product_id):
    print("reachrdf casrd")
    user = request.user
    product = get_object_or_404(Product_item, id=product_id)
    print(product)   
    try:
        if request.user.is_authenticated:
            item = CartItem.objects.get(
                product=product, user = user)
        else:
            cart = Cart.objects.get(cart =_cart_id(request))
            item = CartItem.objects.get(
                product=product, cart=cart )
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    except:
        pass
    referring_page = request.META.get('HTTP_REFERER')
    # Redirect back to the referring page
    return HttpResponseRedirect(referring_page)

def delete_cart(request, product_id):

    product = get_object_or_404(Product_item, id=product_id)
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user = request.user)
            item = CartItem.objects.get(
                product=product, cart = cart)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            item = CartItem.objects.get(
                product=product, cart=cart )
        item.delete()
    except:
        pass
    referring_page = request.META.get('HTTP_REFERER')
    # Redirect back to the referring page
    return HttpResponseRedirect(referring_page)

def checkout_manager(request):
    current_user = request.user
    if current_user.is_authenticated:
        return redirect('store:checkout')
    else:
        return redirect('store:checkout_signin')
    
def checkout_signin(request):
    current_user = request.user
    if current_user.is_authenticated:
        return redirect('store:checkout')
    else:
        if request.method == 'POST':
            loginform = Signin_Form(request.POST)
            if loginform.is_valid():
                login_cred = loginform.cleaned_data['login_cred']
                password = loginform.cleaned_data['password']
                user = account_manager.authenticate(
                    request, email=login_cred, phone=login_cred, username=login_cred, password=password)
                if user is not None:
                    try:
                        cart = Cart.objects.get(cart_id= _cart_id(request))
                        is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                        if is_cart_item_exist:
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item_in_user_cart = CartItem.objects.filter(user = user,product = item.product).exists()
                                if item_in_user_cart:
                                    product = CartItem.objects.get(user = user,product = item.product)
                                    product.quantity = item.quantity
                                    item.delete()
                                    product.save()
                                else:
                                    new_cart_item = CartItem(user=user, quantity=item.quantity, product=item.product)
                                    new_cart_item.save()
                    except:
                        pass
                    auth.login(request, user)
                    return redirect('store:cart')
                else:
                    messages.error(request, 'Invalid login credentials')
                    return HttpResponse('Invalid login credentials')
            else:
                return HttpResponse('form not valid')
        loginform = Signin_Form()
        return render(request,"accounts/checkout_signin.html",{"form":loginform})
    
def checkout_signup(request):
    current_user = request.user
    if current_user.is_authenticated:
        return redirect('store:checkout')   
    else:
        if request.method == 'POST':
            signupform = CustomerRegisterForm(request.POST)
            if signupform.is_valid():
                user = signupform.save()
                wallet = Wallet.objects.create(user=user, balance=100)
                Transaction.objects.create(user=user,amount=100,transaction_type='credit',description='Signup bonus',)
                try:
                    cart = Cart.objects.get(cart_id= _cart_id(request))
                    is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                    if is_cart_item_exist:
                        cart_items = CartItem.objects.filter(cart=cart)
                        for item in cart_items:
                            item.user = user
                            item.cart = None
                            item.save()
                except:
                    pass
                auth.login(request, user)
                return redirect('store:cart')
            else:
                print(signupform.errors)
                return HttpResponse("failed")

        form = CustomerRegisterForm()
        return render(request,"accounts/checkout_signup.html",{"form":form})
    
    
def checkout_signinotp(request):
    if request.method == 'POST':
        login_cred = request.POST.get('login_cred')
        user = account_manager.getuser(
                request, email=login_cred, phone=login_cred, username=login_cred)
        if user is not None:
            request.session['email']=user.email
            verify.send(user.phone)
            otp_form = Otp_Form()
            return render(request, 'store/checkout_otpverification.html', {'form': otp_form , 'user' : user})          
        else:
            messages.error(request, 'Invalid login credentials')
            return HttpResponse('Invalid login credentials')
    return render(request, 'store/signinotp.html')

def checkout_signinotp_verification(request):
    if request.method == 'POST':
        form = Otp_Form(request.POST)
        if form.is_valid():
            UserModel = get_user_model()
            code = form.cleaned_data['otp']
            user = UserModel.objects.get(email=request.session.get('email'))
            print(user.email)
            
            if verify.check(user.phone, code):
                messages.success(request, "OTP verified")
                try:
                    cart = Cart.objects.get(cart_id= _cart_id(request))
                    is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                    if is_cart_item_exist:
                        cart_items = CartItem.objects.filter(cart=cart)
                        for item in cart_items:
                            item_in_user_cart = CartItem.objects.filter(user = user,product = item.product).exists()
                            if item_in_user_cart:
                                product = CartItem.objects.get(user = user,product = item.product)
                                product.quantity = item.quantity
                                item.delete()
                                product.save()
                            else:
                                new_cart_item = CartItem(user=user, quantity=item.quantity, product=item.product)
                                new_cart_item.save()
                except:
                    pass
                auth.login(request, user)
                return redirect('store:cart')
            else:

                error_msg = "Invalid OTP. Please try again later."
                messages.error(request, error_msg)
        else:
            messages.error(request, "Invalid OTP form submission. Please try again.")
    else:
        form = Otp_Form()
    return render(request, 'store/checkout_otpverification.html', {'form': form})

def address_components(request):
        country = Country.objects.all()
        states = State.objects.all()
        addressform = AddressBookForm()
        context = {
            'states' : states,
            'country' : country,
            'addressform' : addressform,    
        }
        return context 
def checkout(request):
    current_user = request.user
    address = AddressBook.objects.filter(user = current_user)
    context = {
        'address' : address,
    }
    context.update(cart_items(request))
    context.update(address_components(request))
    return render(request, 'products/checkout.html',context)

def payment_with_existing_address(request):
    if request.method == 'POST':
        id = request.POST.get('add_id')
        request.session['address_id'] = id 

    return redirect('store:payment')

def payment_with_new_address(request):
    
    if request.method == 'POST':
        
        form = AddressBookForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user 
            address.save()
            request.session['address_id'] = address.id 
        else:
            print(form.errors)
        return redirect('store:payment')
    

from django.core.exceptions import ObjectDoesNotExist
def payment(request):
    address_id = request.session.get('address_id')
    address = AddressBook.objects.get(id = address_id)
    try:
        wallet = Wallet.objects.get(user = request.user)
    except ObjectDoesNotExist:
        wallet = Wallet.objects.create(user=request.user, balance=100)
        Transaction.objects.create(user=request.user,amount=100,transaction_type='credit',description='Signup bonus',)
    
    context = {
        'address' : address,
        'wallet' : wallet,
    }
    context.update(cart_items(request))
    return render(request, 'products/checkout-payment.html',context)


def add_wishlist(request,id):
    return HttpResponse("wishlisted")
    
from django.http import JsonResponse

def check_quantity(request):
    
    if request.method == 'POST':
        data = json.loads(request.body)  # Unpack the JSON data sent in the request body
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity'))
        product = Product_item.objects.get(id= product_id)
        message = None
        in_stock = True
        
        try:
            if request.user.is_authenticated:
                try :
                    cart_item = CartItem.objects.get(
                        product=product, user = request.user)
                except:
                    pass    
            else:
                cart = Cart.objects.get(cart =_cart_id(request))
                try :
                    cart_item = CartItem.objects.get(
                        product=product, cart=cart )
                except:
                    pass
            if cart_item:
                print("dfgdfg")
                if product.quantity >= cart_item.quantity  + quantity:
                    quantity = cart_item.quantity + quantity
                    in_stock = True
                    message = None
                else:
                    in_stock = False
                    message = "Sorry, You have reached the maximum quantity of products ."


        except:
                if product.quantity > quantity:
                    in_stock = True
                else:
                    in_stock = False
                    message = "Sorry, You have reached the maximum quantity of products ."

       
        response_data = {
            'message':message,
            'in_stock': in_stock,
            'quantity':quantity,
        }

    return JsonResponse(response_data)



def get_added(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Unpack the JSON data sent in the request body
        product_id = data.get('product_id')
        product = Product_item.objects.get(id= product_id)
        item = False
        try:
            if request.user.is_authenticated:
                item = CartItem.objects.get(
                    product=product, user = request.user)
            else:
                cart = Cart.objects.get(cart =_cart_id(request))
                item = CartItem.objects.get(
                    product=product, cart=cart )
        except:
            pass
        
        in_stock = False
        if item :
            in_stock = True
            if item.quantity <= product.quantity:
                quantity = item.quantity
                message = False
            else:
                quantity = product.quantity
                message = 'The product is in high demand and there is not enough stock available so the quantity in your cart has been reduced.'  
        else:
            message = False
            quantity = 1
    response_data = {
        'quantity': quantity,
        'inStock': in_stock,
        'message' : message,
       
    }

    return JsonResponse(response_data)


def update_cart_quantity(request):
    print("yeesee")
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('variation_id')
        current_user = request.user
        product = Product_item.objects.get(id=product_id)
        print(product)
        if current_user.is_authenticated:
            cart_item = CartItem.objects.get(user=current_user, product=product)
            cart_item.quantity += 1
            cart_item.save()   
            context = cart_info(request)
            return JsonResponse({'success': True,'total' : cart_item.product.price * cart_item.quantity,'net' : context['net'],'tax' : context['tax'],'g_total' : context['total'],})
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart = cart, product=product)
            cart_item.quantity += 1
            cart_item.save()
            context = cart_info(request)
            return JsonResponse({'success': True,'total' : cart_item.product.price * cart_item.quantity,'net' : context['net'],'tax' : context['tax'],'g_total' : context['total'],})
    return JsonResponse({'success': False})


def decrease_cart_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('variation_id')
        print(product_id)
        current_user = request.user
        product = Product_item.objects.get(id=product_id)
        print(product)
        if current_user.is_authenticated:
            cart_item = CartItem.objects.get(user=current_user, product=product)
            cart_item.quantity -= 1
            cart_item.save()
            context = cart_info(request)
            response_data = {
                'quantity': cart_item.quantity,
                'total' : cart_item.product.price * cart_item.quantity,
                'success' : True, 
                'net': context['net'],
                'g_total' : context['total'],
                'tax' : context['tax']
            }
            
            if cart_item.quantity == 0:
                cart_item.delete()
            return JsonResponse(response_data)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart = cart, product=product)
            cart_item.quantity -= 1
            cart_item.save()
            context = cart_info(request)
            response_data = {
                'quantity': cart_item.quantity,
                'total' : cart_item.product.price * cart_item.quantity,
                'success' : True, 
                'net': context['net'],
                'g_total' : context['total'],
                'tax' : context['tax']
            }
            
            if cart_item.quantity == 0:
                cart_item.delete()
            return JsonResponse(response_data)
        
    return JsonResponse({'success': False})

def decrease_cart_quantity_os(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('variation_id')
        print(product_id)
        current_user = request.user
        product = Product_item.objects.get(id=product_id)
        print(product)
        if current_user.is_authenticated:
            cart_item = CartItem.objects.get(user=current_user, product=product)
            cart_item.quantity -= 1
            cart_item.save()
            context = cart_info(request)
            response_data = {
                'name': cart_item.product.product.name,
                'id' : cart_item.product.id,
                'image' : cart_item.product.image.url,
                'size' : cart_item.product.size,
                'price' : cart_item.product.price,
                'total' : cart_item.quantity * cart_item.product.price,
                'net' : context['net'],
                'tax' : context['tax'],
                'quantity': cart_item.quantity,
                'success' : True ,
                'g_total' : context['total'],
            }
            if cart_item.quantity <= product.quantity:
                response_data['in_stock'] = True
            else:
                response_data['in_stock'] = False
            if cart_item.quantity == 0:
                cart_item.delete()
            return JsonResponse(response_data)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart = cart, product=product)
            cart_item.quantity -= 1
            cart_item.save()
            context = cart_info(request)

            response_data = {
                'name': cart_item.product.product.name,
                'id' : cart_item.product.id,
                'image' : cart_item.product.image.url,
                'size' : cart_item.product.size,
                'price' : cart_item.product.price,
                'total' : cart_item.quantity * cart_item.product.price,
                
                'quantity': cart_item.quantity,
                'success' : True ,
                'net' : context['net'],
                'tax' : context['tax'] ,
                'g_total' : context['total'],
            }
            if cart_item.quantity <= product.quantity:
                response_data['in_stock'] = True
            else:
                response_data['in_stock'] = False
            if cart_item.quantity == 0:
                cart_item.delete()
            
            return JsonResponse(response_data)
        
    return JsonResponse({'success': False})


def check_quantity_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Unpack the JSON data sent in the request body
        product_id = int(data.get('product_id'))
        product = Product_item.objects.get(id= product_id)
        message = None
        in_stock = True
        quantity = None
        try:
            if request.user.is_authenticated:
                try :
                    cart_item = CartItem.objects.get(
                        product=product, user = request.user)
                except:
                    pass
                        
            else:
                cart = Cart.objects.get(cart =_cart_id(request))
                
                try :
                    cart_item = CartItem.objects.get(
                        product=product, cart=cart )
                except:
                    pass
        except:
            pass
        try:
            if cart_item:
                if product.quantity > cart_item.quantity:
                    in_stock = True
                    message = None
                    quantity = cart_item.quantity
                else:
                    in_stock = False
                    message = "Sorry, You have reached the maximum quantity of products ."
                    quantity = cart_item.quantity
        except:
            pass

        response_data = {
            'message':message,
            'inStock': in_stock,
            'quantity' : quantity,
        }

    return JsonResponse(response_data)

def quantity_check(request):
    if request.method == 'POST':
        print("hooi")
        data = json.loads(request.body)  # Unpack the JSON data sent in the request body
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity'))
        product = Product_item.objects.get(id= product_id)
        message = None
        in_stock = True
        try:
            if request.user.is_authenticated:
                try :
                    cart_item = CartItem.objects.get(
                        product=product, user = request.user)
                except:
                    pass
                        
            else:
                cart = Cart.objects.get(cart =_cart_id(request))
                
                try :
                    cart_item = CartItem.objects.get(
                        product=product, cart=cart )
                except:
                    pass
        except:
            pass
        try:
            if cart_item:
                if product.quantity >= cart_item.quantity + quantity:
                    in_stock = True
                    message = None
                else:
                    in_stock = False
                    message = "Sorry, You have reached the maximum quantity of products ."
        except:
            pass

        response_data = {
            'message':message,
            'inStock': in_stock,
        }

    return JsonResponse(response_data)
    
        # rzp_test_0cr8VAzWXYja52

def apply_coupon(request):
    if request.method == "GET":
        coupon_code = request.GET.get('coupon')
        total = request.GET.get('total')
        total = total.replace('₹', '').replace(',', '')
        # Convert the total value to a float
        total = float(total)
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                verify_coupon_exists = Verify_coupon.objects.filter(user=request.user, coupon=coupon).exists()
                if verify_coupon_exists:
                    verify_coupon = Verify_coupon.objects.get(user= request.user , coupon = coupon)
                    if coupon.uses <= verify_coupon.uses:
                        return JsonResponse({'failed': 'You Have Used Up This Coupon '})
                    if coupon.min_amount > total:
                        return JsonResponse({'failed': ' Minimum Cart Value for Applaying This Coupon Is ' +str(coupon.min_amount)+'. Add More Products And Try Again'})
                discounted_price = total - min((total/100)*coupon.discount,coupon.max_discount)
                print(discounted_price)
                
                return JsonResponse({'success': 'Coupon verified successfully!  '+str(total-discounted_price)   +   '  has been reduced','total':discounted_price})
            except Coupon.DoesNotExist:
                return JsonResponse({'error': 'Invalid coupon code'})

    return JsonResponse({'error': 'Invalid request'})

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def catcom(request):
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    context = {
        'categories':categories,
        'tags' : tags
    }
    return context