from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import AddressBook
from products.models import Category, Product_Tags, Products_Table, Product_item, Product_images,P_tags,ProductClassification,classfiedProducts
from accounts.models import Cart, CartItem
# Create your views here.


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
    product = Products_Table.objects.all()
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()

    context = {
        'product': product,
        'categories': categories,
        'tags': tags,
    }
    context.update(cart_items(request))

    return render(request, 'products/productlist.html', context)


def allproducts(request):

    product = Products_Table.objects.all()
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()

    context = {
        'product': product,
        'categories': categories,
        'tags': tags,
    }
    context.update(cart_items(request))

    return render(request, 'products/productlist.html', context)

def product_by_tags(request,tag_name):
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    tag = Product_Tags.objects.get(tag_name = tag_name)
    # # product = Products_Table.objects.filter(p_tags_set__tag__tag_name=tag_name)
    # product = P_tags.objects.filter(p_tags__tag=tag)
    p_t = tag.p_tags_set.all()
    product = []
    for o in p_t:
        product.append(o.product)

    context = {
        'product': product,
        'categories': categories,
        'tags': tags,
    }
    context.update(cart_items(request))

    return render(request, 'products/productlist.html', context)


def product_detail(request, category, slug, id):
    product = Products_Table.objects.get(id=id)
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    varients = Product_item.objects.filter(product=product)
    images = Product_images.objects.filter(product=product)

    related_prod = Products_Table.objects.filter(
        category__category_name=category)

    context = {
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

    return render(request, 'products/profile.html')


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


def cart_items(request, total=0, quantity=0, cart_items=None):

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
    print("hello")
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
                cart_item.quantity = cart_item.quantity + quantity
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
            print("authenticate")

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


def classifiedproducts(request,id):
    categories = Category.objects.all()
    tags = Product_Tags.objects.all()
    classification = ProductClassification.objects.get(id = id)
    class_products = classfiedProducts.objects.filter(classification=classification)
    product = []
    for p in class_products:
        product.append(p.product)
    context = {
        'product': product,
        'categories': categories,
        'tags': tags,
    }
    context.update(cart_items(request))

    return render(request, 'products/productlist.html', context)


def checkout_manager(request):
    current_user = request.user
    if current_user.is_authenticated:
        return redirect('store:checkout')
    else:
        return redirect('store:checkout_signup')
    
def checkout(request):
    current_user = request.user
    address = AddressBook.objects.filter(user = current_user)
    
    context = {
        'address' : address,
    }
    context.update(cart_items(request))
    return render(request, 'products/checkout.html',context)

def payment(request):
    current_user = request.user
    address = AddressBook.objects.filter(user = current_user)
    
    context = {
        'address' : address,
    }
    context.update(cart_items(request))
    return render(request, 'products/checkout-payment.html',context)



        