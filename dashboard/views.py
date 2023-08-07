from datetime import timedelta
from io import BytesIO
from django.shortcuts import render
from django.shortcuts import redirect, render , get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from products.models import P_tags
from products.models import Product_Tags, Products_Table, Product_item,Product_images
from products.forms import CategoryForm, ProductsTableForm, ProductsTags, ProductItemForm, ProductTagForm ,ProductItemUpdateForm
from products.models import Category
from orders.models import Order,OrderProduct
from django.db import IntegrityError
from django.contrib import messages
from accounts.models import User_Accounts
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from accounts.models import CartItem
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Coupon
from .forms import CouponForm
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date
from django.db.models import Sum
from reportlab.pdfgen import canvas
from dashboard.models import CarouselItem

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from store . views import address_components
# def custom_404(request , exception):
#     return render(request,'404.html',status=404)
def is_superuser(request):
    user = request.user
    if user.is_superuser:
        return True
    return False

# Create your views here.
def get_month_name(month):
    months_in_english = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    return months_in_english[month]

@login_required(login_url='accounts:signin')
def dashboard(request):
    if not is_superuser(request):
        return redirect('store:home')
    orders = Order.objects.filter(status = "Delivered")
    total_rev = 0
    total_this = 0
    recent_users = User_Accounts.objects.filter().order_by('created_at')[:3]
    recent_act = Order.objects.exclude(status="new").order_by('-created_at')[:3]
    for i in orders:
        total_rev += i.order_total
    current_datetime = timezone.now()
    orders_this_month = Order.objects.filter(
            status="Delivered",
            deliverd_at__year=current_datetime.year,
            deliverd_at__month=current_datetime.month)
    for i in orders_this_month:
        total_this += i.order_total
    
    current_datetime = timezone.now()
    start_date = current_datetime - timedelta(days=180)
    data = [['Month', 'New User Signups', 'New Orders']]
    while start_date < current_datetime:
        end_date = start_date.replace(day=1) + timedelta(days=31)
        new_user_signups = User_Accounts.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
        new_orders = Order.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
        month_name = get_month_name(start_date.month)
        data.append([month_name, new_user_signups, new_orders])
        start_date = end_date
    for i in data:
        print(i)

        
    context = {
        'no_orders': len(Order.objects.filter(status="Delivered")),
        'total_rev': total_rev,
        'total_this': total_this,
        'data': data,
        'recent_users':recent_users,
        'recent_act' : recent_act
    }
    return render(request, 'dashboard/index.html',context)

@login_required(login_url='accounts:signin')
def usermanager(request):
    if not is_superuser(request):
        return redirect('store:home')
    return render(request, 'users.html')

@login_required(login_url='accounts:signin')
def products(request):
    if not is_superuser(request):
        return redirect('store:home')
    search = request.POST.get('search')
    category = request.POST.get('category')
    categories = Category.objects.all()
    products = Products_Table.objects.all()
    
    if category:
        try:
            cat = Category.objects.get(category_name=category)
            products = products.filter(category=cat)
        except Category.DoesNotExist:
            pass
    
    if search:
        products = products.filter(name__icontains=search)

    paginator = Paginator(products, 12)
    total_pages = paginator.num_pages
    
    pagenum = request.POST.get('num')
    productFinal = paginator.get_page(pagenum) if pagenum else paginator.get_page(1)
    for i in productFinal:
        print(i)
        
    context = {
         'products': productFinal,
         'pages': total_pages,
         'categories': categories,
     }

    return render(request, 'dashboard/page-products-grid.html', context)

@login_required(login_url='accounts:signin')
def addproduct(request):
    if not is_superuser(request):
        return redirect('store:home')
  
    # print(Products_Table.objects.filter(producttag__tag__tag_name='hello'))
    categories = Category.objects.filter(is_child=True)
    tags = Product_Tags.objects.all()
    product_tags_form = ProductTagForm()
    product_item_form = ProductItemForm()
    products_table_form = ProductsTableForm()
    size_choice = Product_item.SIZE_CHOICES
    context = {'product_form': products_table_form, 'product_item': product_item_form,
               'categories': categories, 'tags': tags, 'products': products, 'tagform': product_tags_form, 'size_choice': size_choice,}
    return render(request, 'dashboard/addproducts.html', context)

@login_required(login_url='accounts:signin')
def addnewproduct(request):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        form = ProductsTableForm(request.POST, request.FILES)
        formtag = ProductTagForm(request.POST)
        if form.is_valid() and formtag.is_valid():
            name = form.cleaned_data['name']
            slug = form.cleaned_data['slug']
            selected_options = formtag.cleaned_data.get('options', [])
            if Products_Table.objects.filter(name=name).exists() or \
                    Category.objects.filter(slug=slug).exists():
                # Return an error message or handle the error as needed
                return redirect('dashboard:addproduct')
            product = form.save()
            for tag_id in selected_options:
                tag = Product_Tags.objects.get(id=tag_id)
                product_tag = P_tags(product=product, tag=tag)
                product_tag.save()

            return redirect('dashboard:addproduct')
        else:
            print(form.errors)
            print(formtag.errors)
    return redirect('dashboard:addproduct')

@login_required(login_url='accounts:signin')
def addproductitems(request):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        form = ProductItemForm(request.POST)
        if form.is_valid():
            try:
                product_item = form.save()
                product = product_item.product
                product_id = product.id 
                messages.success(request, 'Product items added successfully.')
                print(product_item.product)
                return redirect('dashboard:productdetails',product_id)
            except IntegrityError as e:
                error_message = f"Error creating product image: {str(e)}"
                messages.error(request, error_message)
        else:
            messages.error(request, 'Error in form submission.')
            print(form.errors)
    return redirect('dashboard:pro')

        
@login_required(login_url='accounts:signin')
def orders(request):
    if not is_superuser(request):
        return redirect('store:home')
    orders_list = Order.objects.filter(is_ordered=True).exclude(status="New").order_by('-created_at')
    paginator = Paginator(orders_list,12)
    page_number = 1
    if request.method == 'POST':
        page_number = request.POST.get('page')
        # status = request.POST.get('status')
        # if status:
        #     orders_list = Order.objects.filter(is_ordered=True,status="status").order_by('-created_at') 
        #     paginator = Paginator(orders_list,12) 
    productFinal = paginator.get_page(page_number)
    total_pages = range(1, paginator.num_pages + 1)
    context = {
        'orders' : productFinal,
        'total_pages' :total_pages,
        'curr' :page_number
    }
    
    return render(request, 'dashboard/orders.html',context)
from accounts.models import Wallet,Transaction

def change_order_status(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    order_ = Order.objects.get(order_number = id)
    status = request.POST.get('status')
    print(status)
    user = order_.user
    print(user)
    if status == "Delivered":
        order_.deliverd_at = timezone.now()
        user = order_.user
        print(user)
        total =  order_.order_total
        applicable_spikes = total//10
        try:
            wallet = Wallet.objects.get(user = user)
        except:
            wallet = Wallet.objects.create(user = user , balance = 100 )
            Transaction.objects.create(user = user , amount = 100 , transaction_type = 'credit' , description = 'Login Bounus')
        wallet.balance += applicable_spikes
        wallet.save()
        Transaction.objects.create(user = user , amount = applicable_spikes , transaction_type = 'credit' , description = 'Purchase bonus for the order ref no'+str(order_.order_number))

        
    elif status == "Returned" :
        order_.returned_at = timezone.now()
        try:
            wallet = Wallet.objects.get(user = user)
        except:
            wallet = Wallet.objects.create(user = user , balance = 100 )
            Transaction.objects.create(user = user , amount = 100 , transaction_type = 'credit' , description = 'Login Bounus')
        total =  order_.order_total
        total -= order_.payment.coupon_discount

        trans = Transaction.objects.create(user = request.user , amount = discount , transaction_type = 'credit' ,
                    description = 'Refund for cancelled order ref number'+str(order_.order_number))
        trans.save()
        Transaction.objects.create(user = user , amount = total , transaction_type = 'credit' , description = 'Refund for returned order')
        
    elif status == "Cancelled" :
        if order_.payment.payment_method =="cod":
            spike = order_.payment.spike_use
            if spike:
                discount = order_.payment.spike_discount
                wallet = Wallet.objects.get(user = request.user)
                wallet.balance += discount
                if discount > 0:
                    trans = Transaction.objects.create(user = request.user , amount = discount , transaction_type = 'credit' ,
                                description = 'Refund for cancelled order ref number'+str(order_.order_number))
                trans.save()
        if order_.payment.payment_method =="razorpay":
            total =  order_.order_total
            wallet = Wallet.objects.get(user = request.user)
            wallet.balance += total
            wallet.save()
            Transaction.objects.create(user = user , amount = total , transaction_type = 'credit' , description = 'Refund for Cancelled order')
            
    else:
        order_.deliverd_at = None
    if status:
        order_.status = status
    order_.save()

    return redirect('dashboard:orders')

@login_required(login_url='accounts:signin')
def tagsandcategory(request):
    if not is_superuser(request):
        return redirect('store:home')
    categories = Category.objects.all()
    category_form = CategoryForm()
    tag_form = ProductsTags()
    context = {'category_form': category_form,
               'tag_form': tag_form, 'categories': categories}
    return render(request, 'addcategory.html', context)

@login_required(login_url='accounts:signin')
def addcategory(request):
    if not is_superuser(request):
        return redirect('store:home')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            slug = form.cleaned_data['slug']
            if Category.objects.filter(category_name=category_name).exists() or \
                    Category.objects.filter(slug=slug).exists():
                # Return an error message or handle the error as needed
                return render(request, 'dashboard/addcategory.html', {'form': form, 'error': 'Category already exists'})
            form.save()
        print(form.errors)
    categories = Category.objects.all()
    category_form = CategoryForm()
    
    context = {'category_form': category_form,
                'categories': categories}
    return render(request, 'dashboard/addcategory.html', context)

@login_required(login_url='accounts:signin')
def addtags(request):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        form = ProductsTags(request.POST)
        if form.is_valid():
            tag_name = form.cleaned_data['tag_name']
            slug = form.cleaned_data['slug']
            if Product_Tags.objects.filter(tag_name=tag_name).exists() or Product_Tags.objects.filter(slug=slug).exists():
                # Return an error message or handle the error as needed
                return render(request, 'dashboard/addtags.html', {'form': form, 'error': 'Tag already exists'})
            form.save()
            print('saved')
        else:
            print(form.errors)   
    tag_form = ProductsTags()
    tags = Product_Tags.objects.all()
    context = {
               'tags' : tags,
               'tag_form': tag_form,}
    return render(request, 'dashboard/addtags.html', context)

@login_required(login_url='accounts:signin')
def edit_category(request, category_id):
    if not is_superuser(request):
        return redirect('store:home')
    category = get_object_or_404(Category, id=category_id)
    print(category)
    if request.method == 'POST':
        print("wtf")
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            print("saved")
            form.save()
            return redirect('dashboard:addcategory')  # Replace 'category_list' with the URL name of your category list view
        print(form.errors)
    else:
        form = CategoryForm(instance=category)
        print(form.errors)
    
    return redirect('dashboard:addcategory')

@login_required(login_url='accounts:signin')
def delete_category(request, category_id):
    if not is_superuser(request):
        return redirect('store:home')
    print("reachedd delete")
    category = get_object_or_404(Category, id=category_id)
    print(category)
    if request.method == 'POST':
        category.delete()
        return redirect('dashboard:addcategory')  # Replace 'category_list' with the URL name of your category list view
    return redirect('dashboard:addcategory')

@login_required(login_url='accounts:signin')   
def edit_tags(request, tag_id):
    if not is_superuser(request):
        return redirect('store:home')
    tag = get_object_or_404(Product_Tags, id=tag_id)

    if request.method == 'POST':
        print("wtf")
        form = ProductsTags(request.POST, instance=tag)
        if form.is_valid():
            print("saved")
            form.save()
            return redirect('dashboard:addtags')  # Replace 'category_list' with the URL name of your category list view
        print(form.errors)
    else:
        form = CategoryForm(instance=tag)
        print(form.errors)
    
    return redirect('dashboard:addtags')

@login_required(login_url='accounts:signin')
def delete_tags(request, tag_id):
    if not is_superuser(request):
        return redirect('store:home')
    print("reachedd delete")
    tag = get_object_or_404(Product_Tags, id=tag_id)

    if request.method == 'POST':
        tag.delete()
        return redirect('dashboard:addtags')  # Replace 'category_list' with the URL name of your category list view
    return redirect('dashboard:addtags')

@login_required(login_url='accounts:signin')
def delete_product(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    try:
        product = Products_Table.objects.get(id=id)
        product_items = Product_item.objects.filter(product = product)
        for item in product_items:
            CartItem.objects.filter(product= item).delete()
        product.delete()
        messages.success(request, "Product deleted successfully.")
    except product.DoesNotExist:
        messages.error(request, "Product does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('dashboard:products')

@login_required(login_url='accounts:signin')
def changestatus(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    try:
        product = Products_Table.objects.get(id=id)
        if product.is_active:
            product.is_active = False
        else:
            product.is_active = True
        product.save()
    except product.DoesNotExist:
        messages.error(request, "Product does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('dashboard:products')

@login_required(login_url='accounts:signin')
def status(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    try:
        product = Products_Table.objects.get(id=id)
        if product.is_active:
            product.is_active = False   
        else:
            product.is_active = True
        product.save()
        messages.success(request, "Product status changed.")
    except product.DoesNotExist:
        messages.error(request, "Product does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('dashboard:products')

@login_required(login_url='accounts:signin')
def productdetails(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    product = Products_Table.objects.get(id = id)
    variations = Product_item.objects.filter(product = product)
    images = Product_images.objects.filter(product = product)
    vform = ProductItemForm()
    itemupdate=ProductItemUpdateForm()
    size_choice = Product_item.SIZE_CHOICES
    context = {
         'product':product,
         'variations' : variations,
         'images' : images,
         'form' : vform,
         'size_choice' : size_choice,
         'itemupdate' : itemupdate,

     }

    return render(request, 'dashboard/page-seller-detail.html',context)

@login_required(login_url='accounts:signin')
def update_product_item(request, product_item_id):
    if not is_superuser(request):
        return redirect('store:home')
    print("yererf")
    product_item = Product_item.objects.get(id=product_item_id)
    if request.method == 'POST':
        form = ProductItemUpdateForm(request.POST)
        if form.is_valid():
            product_item.price = form.cleaned_data['price']
            product_item.quantity = form.cleaned_data['quantity']
            status = form.cleaned_data['status']
            if status == 'active':
                product_item.is_active = True
            else:
                product_item.is_active = False
            product_item.save()
    referring_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(referring_page)



@login_required(login_url='accounts:signin')
def pro(request):
    if not is_superuser(request):
        return redirect('store:home')
    products = Products_Table.objects.all()
    context = {
         'products':products,
     }

    return render(request, 'dashboard/page-products-grid.html',context)


@login_required(login_url='accounts:signin')
def deleteimage(request,id,image_id):
    if not is_superuser(request):
        return redirect('store:home')
    product = Products_Table.objects.get(id = id)
    image = Product_images.objects.get(product = product , id = image_id)
    image.delete()
    referring_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(referring_page)


@login_required(login_url='accounts:signin')
def upload_image(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        image_data = request.POST.get('image')
        product = Products_Table.objects.get(id = id)
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')

        try:
            product_image = Product_images()
            product_image.product = product
            product_image.image = image_file
            product_image.save()
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Value too long for image field.'})
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required(login_url='accounts:signin')
def changethumbnail(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        image_data = request.POST.get('image')
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')

        try:
            product = Products_Table.objects.get(id = id)
            product.image = image_file
            product.save()
        except :
            return JsonResponse({'success': False, 'error': 'Value too long for image field.'})
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



# def changethumbnail(request,id):
#     if request.method == 'POST':
#         product = Products_Table.objects.get(id = id)
#         new_thumbnail = request.FILES['thumbnail']
#         product.image = new_thumbnail
#         product.save()
#     referring_page = request.META.get('HTTP_REFERER')
#     return HttpResponseRedirect(referring_page)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------USER MANAGER-----------------------------------------------------------------------------------------------------

    """functions for managing users like delete create block or unblock ......
    """


# def users(request):
#     if 'email' in request.session:
#         users = User_Accounts.objects.filter(is_superuser=False).order_by('id').reverse()
#         context = {
#             'users': users,
#         }
#         return render(request,'dashboard/users',context)
#     return redirect('signin')

@login_required(login_url='accounts:signin')
def users(request):
    if not is_superuser(request):
        return redirect('store:home')
    users = User_Accounts.objects.filter(is_superuser=False).order_by('id').reverse()
    context = {
        'users': users,
    }
    return render(request,'dashboard/users.html',context)

@login_required(login_url='accounts:signin')
def userdetails(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    user = User_Accounts.objects.get(id = id)
    # context = {
    #     'user' : user,
    # }
    # return render(request,'dashboard/userdetails.html',context)
    return HttpResponse(user.username)
    


@login_required(login_url='accounts:signin')
def change_user_status(request, name):
    if not is_superuser(request):
        return redirect('store:home')
    user = User_Accounts.objects.get(username=name)
    status = request.POST.get('status')
    print(user)
    print(status)
    
    if status:
        user.account_status = status
        user.save()
    print(user.account_status)
    return redirect('dashboard:users')


@login_required(login_url='accounts:signin') 
def coupons(request):
    if not is_superuser(request):
        return redirect('store:home')
    coupon = Coupon.objects.all().order_by('-created_at')
    context = {
        'coupon': coupon,
    }
    
    return render(request, 'dashboard/coupon.html',context)

@login_required(login_url='accounts:signin')
def add_coupons(request):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == "POST":
        form = CouponForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon added successfully.')
            return redirect('dashboard:coupons')
        else:
            messages.error(request, 'Error: Invalid data. Please check the form.')
    else:
        form = CouponForm()
    coupon = Coupon.objects.all().order_by('-created_at')
    context = {
        "form": form,
        'coupon': coupon,
    }
    return render(request, 'dashboard/add_coupon.html', context)

@login_required(login_url='accounts:signin')
def activate_coupon(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        pi = Coupon.objects.get(id=id)
        pi.active = True
        pi.save()
        messages.success(request, 'Coupon activated successfully.')
    return redirect('dashboard:coupons')

@login_required(login_url='accounts:signin')
def disable_coupon(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        pi = Coupon.objects.get(id=id)
        pi.active = False
        pi.save()
        messages.success(request, 'Coupon disabled successfully.')
    return redirect('dashboard:coupons')

from io import BytesIO
import uuid
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.conf import settings

class SalesReportPDFView(View):
    def save_pdf(self,params:dict):
        template = get_template("sales_report.html")
        html = template.render(params)
        response = BytesIO()
        pdf =pisa.pisaDocument(BytesIO(html.encode('UTF-8')),response)
        
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf'),True
        return '',None
    # @login_required(login_url='accounts:signin')
    def get(self, request, *args, **kwargs):
        # if not is_superuser(request):
        #     return redirect('store:home')
        total_users = len(User_Accounts.objects.all())
        new_orders = len(Order.objects.all().exclude(status="new"))
        revenue_total = 0
        delivered_orders = Order.objects.filter(status="Delivered")
        for order in delivered_orders:
            revenue_total += order.order_total
        current_date = date.today()
        delivered_orders_this_month = Order.objects.filter(
            status="Delivered",
            deliverd_at__year=current_date.year,
            deliverd_at__month=current_date.month
        )
        month_len = len(delivered_orders_this_month)
        revenue_this_month = delivered_orders_this_month.aggregate(Sum('order_total'))['order_total__sum']
        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

        # return response
        params = {
            'total_users' :total_users,
            'new_orders' : new_orders,
            'revenue_total' : revenue_total,
            'd_month' :delivered_orders_this_month,
            'd_month_len' : month_len,
            'revenue_this_month' : revenue_this_month,
             
        }
        file_name, success = self.save_pdf(params)
        
        if success:
            response = HttpResponse(file_name, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
            return response
        else:
            # Handle error case here, like displaying an error message to the user.
            return HttpResponse("Failed to generate the invoice.", status=500)



@login_required(login_url='accounts:signin')
def carosal(request):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        main_text = request.POST.get('main')
        print(main_text)
        main_text_left = request.POST.get('mainleft')
        sub_text = request.POST.get('subtext')
        about = request.POST.get('About')
        image = request.FILES.get('image')
        print(main_text_left)
        print(sub_text)
        print(main_text)
        if main_text and main_text_left and sub_text and about and image:
            CarouselItem.objects.create(
                main_text=main_text,
                main_text_1=main_text_left,
                sub_text=sub_text,
                about=about,
                image=image
            )
            message = "Form submitted successfully!"
        else:
            message = "Please fill in all the required fields."
        carosals = CarouselItem.objects.filter()
        return render(request, 'dashboard/coustomize.html', {'message': message,'carosals':carosals})
    carosals = CarouselItem.objects.filter()
    return render(request,'dashboard/coustomize.html',{'carosals':carosals})


@login_required(login_url='accounts:signin')
def cursol_stat(request,cid):
    if not is_superuser(request):
        return redirect('store:home')

    c = CarouselItem.objects.get(id = int(cid))
    try:
        if c.active:
            c.active = False
        else :
            c.active = True
        
        messages.success(request, "Status changed successfully!")
        c.save()
    except:
        messages.success(request, "something went wrong!")
    return redirect('dashboard:carosal')
    
    
from products.models import classfiedProducts,ProductClassification
@login_required(login_url='accounts:signin')  
def sales(request):
    if not is_superuser(request):
        return redirect('store:home')
    types_ = ProductClassification.objects.all()
    context = {
        'type' : types_
    }
    return render (request,'dashboard/sales.html',context)


@login_required(login_url='accounts:signin')  
def sales_status(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    c = ProductClassification.objects.get(id = int(id))
    try:
        if c.active:
            c.active = False
        else :
            c.active = True
        
        messages.success(request, "Status changed successfully!")
        c.save()
    except:
        messages.success(request, "something went wrong!")
    return redirect('dashboard:sale')
    

@login_required(login_url='accounts:signin')  
def sales_delete(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    c = ProductClassification.objects.get(id = int(id))
    c.delete()
    messages.success(request, "something went wrong!")
    return redirect('dashboard:sale')
    
    
@login_required(login_url='accounts:signin')  
def sales_edit(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    classification = ProductClassification.objects.get(id = id)
    class_products = classfiedProducts.objects.filter(classification=classification)
    products = Products_Table.objects.all()
    plants = Products_Table.objects.all().exclude(is_active = False)
    cproduct = []
    for p in class_products:
        cproduct.append(p.product)
    context = {
        'cpro' :cproduct ,
        'products' :products,
        'classification' :classification,
        'products' :class_products,
        'plants':plants
        
    }
    return render(request,'dashboard/salesinfo.html',context)

@login_required(login_url='accounts:signin')
def add_sale(request):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        title = request.POST.get('title')
        tagline = request.POST.get('tagline')
        image = request.FILES.get('image')

        if title and tagline and image:
            ProductClassification.objects.create(
                title=title,
                tagline=tagline,
                photo=image
            )
            message = "Form submitted successfully!"
        else:
            message = "Please fill in all the required fields."
    return redirect('dashboard:sale')

import json
@login_required(login_url='accounts:signin')
def add_plants_to_sale(request,id):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        sale = ProductClassification.objects.get(id = id)
        offer = request.POST.get('discount')
        selected_Plants = request.POST.getlist('selectedPlants')
        for i in selected_Plants:
            product = Products_Table.objects.get(id = int(i))
            try:
                temp = classfiedProducts.objects.create(classification = sale , product = product , offer = int(offer))
                temp.save()
            except:
                pass
            
        
    products = Products_Table.objects.all()
    plants = Products_Table.objects.all().exclude(is_active = False)
    class_products = classfiedProducts.objects.filter(classification=sale)
    cproduct = []
    for p in class_products:
        cproduct.append(p.product)
    context = {
        'cpro' :cproduct ,
        'products' :products,
        'classification' :sale,
        'products' :class_products,
        'plants':plants
        
    }
    return render(request,'dashboard/salesinfo.html',context)

@login_required(login_url='accounts:signin')
def delete_sale_product(request,p_id,s_id):
    if not is_superuser(request):
        return redirect('store:home')
    item = classfiedProducts.objects.filter(product = p_id ,classification = s_id )
    item.delete()
    return redirect('dashboard:sales_edit', s_id)

 

    