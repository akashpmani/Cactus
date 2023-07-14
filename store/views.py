import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import AddressBook,Country, State
from products.models import Category, Product_Tags, Products_Table, Product_item, Product_images,P_tags,ProductClassification,classfiedProducts
from accounts.models import Cart, CartItem
from accounts.forms import AddressBookForm,CustomerRegisterForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core import serializers
from .serilizers import Product_itemSerializer
from rest_framework.renderers import JSONRenderer
import json
from django.core.serializers.json import DjangoJSONEncoder
# Create your views here.



def search_view(request):
    query = request.GET.get('q', '')
    results = Products_Table.objects.filter(name__icontains=query)[:5]
    search_results = [{'name': product.name, 'image': product.image.url, 'slug': product.slug} for product in results]
    return JsonResponse(search_results, safe=False)


def home(request):
    current_user = request.user
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    classification = ProductClassification.objects.all()
    
    context = {
        'categories': categories,
        'tags': tags,
        'classification' : classification,
        
    }
    context.update(cart_items(request))
    return render(request, 'products/index.html', context)

def products(request):
    product = Product_item.objects.order_by('id')
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()   
    paginator = Paginator(product, 1)
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


def allproducts(request):

    product = Products_Table.objects.order_by('id')
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    paginator = Paginator(product,1)
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
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart.id)
        total_price = 0
        product_data = []
        for item in cart_items:
            product_item = item.product
            id = product_item.id
            product_table = product_item.product
            size = product_item.size
            price = product_item.price
            total_price += price
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
            }
            product_data.append(product_dict)
        tax = round(total_price * 0.4, 3)
        total_price += tax
        tax = {
            'cart_items' : cart_items,
            'total': total_price,
            'tax': tax,
        }
    except Cart.DoesNotExist:
        pass

    context = {
        'product_data': product_data,
        'tax': tax,
    }
    return render(request,"products/cart.html",context)

def cart_items2(request, total=0, quantity=0, cart_items=None):

    current_user = request.user
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        total_price = 0
        product_data = []
        products = []
        for item in cart_items:
            product_item = item.product
            products.append(product_item)
            product_table = product_item.product
            size = product_item.size
            price = product_item.price
            total_price += price
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
        tax = round(total_price * 0.4, 3)
        total_price += tax
       
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

    return context

def cart_items(request, total=0, quantity=0, cart_items=None):

    current_user = request.user
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        total_price = 0
        product_data = []
        products = []
        for item in cart_items:
            product_item = item.product
            products.append(product_item)
            product_table = product_item.product
            size = product_item.size
            price = product_item.price
            total_price += price
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
        tax = round(total_price * 0.4, 3)
        total_price += tax
        tax = {
            'total': total_price,
            'tax': tax,
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
            print(product)

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
        return redirect('store:checkout_signup')

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
        print("yep")
        form = AddressBookForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user 
            address.save()
            request.session['address_id'] = address.id 
        else:
            print(form.errors)
        return redirect('store:payment')
    


def payment(request):
    address_id = request.session.get('address_id')
    address = AddressBook.objects.get(id = address_id)
    context = {
        'address' : address,
        
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
            return JsonResponse({'success': True})
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart = cart, product=product)
            cart_item.quantity += 1
            cart_item.save()
            return JsonResponse({'success': True})
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
            response_data = {
                'quantity': cart_item.quantity,
                'success' : True  
            }
            if cart_item.quantity == 0:
                cart_item.delete()
            return JsonResponse(response_data)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart = cart, product=product)
            cart_item.quantity -= 1
            cart_item.save()
            response_data = {
                'quantity': cart_item.quantity,
                'success' : True  
            }
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