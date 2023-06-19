from django.shortcuts import render
from django.shortcuts import redirect, render , get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from products.models import P_tags
from products.models import Product_Tags, Products_Table, Product_item,Product_images
from products.forms import CategoryForm, ProductsTableForm, ProductsTags, ProductItemForm, ProductTagForm
from products.models import Category
from django.db import IntegrityError
from django.contrib import messages
from accounts.models import User_Accounts
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile

# Create your views here.


def dashboard(request):
    return render(request, 'dashboard/index.html')


def usermanager(request):
    return render(request, 'users.html')


def products(request):
    
    products = Products_Table.objects.all()
    size_choice = Product_item.SIZE_CHOICES
    product_variants = []
    for product in products:
        product_items = product.product_item_set.all()
        product_data = {
            'product': product,
            'product_items': product_items,
            
        }
        product_variants.append(product_data)
    context = {
         'products':products,
          'product_variants': product_variants,
          'size_choice': size_choice,
     }
    
    return render(request, 'dashboard/deummy.html',context)    
    # return render(request, 'dashboard/productlist.html',context)


def addproduct(request):
  
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


def addnewproduct(request):
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


def addproductitems(request):
    if request.method == 'POST':
        form = ProductItemForm(request.POST)
        
        images = request.FILES.getlist('photo')
        # images = request.FILES.getlist('cropped_images')
        if form.is_valid():
            try:
                for image in images:
                    print('image')
                    Product_images.objects.create(
                    product=form.cleaned_data['product'],
                    image=image)
                form.save()
                messages.success(request, 'Product items added successfully.')
                return redirect('dashboard:products')
            except IntegrityError as e:
                error_message = f"Error creating product image: {str(e)}"
                messages.error(request, error_message)
        else:
            messages.error(request, 'Error in form submission.')
            print(form.errors)
    return redirect('dashboard:products')

def orders(request):
    return render(request, 'orders.html')


def tagsandcategory(request):
    categories = Category.objects.all()
    category_form = CategoryForm()
    tag_form = ProductsTags()
    context = {'category_form': category_form,
               'tag_form': tag_form, 'categories': categories}
    return render(request, 'addcategory.html', context)


def addcategory(request):

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


def addtags(request):
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


def edit_category(request, category_id):
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

def delete_category(request, category_id):
    print("reachedd delete")
    category = get_object_or_404(Category, id=category_id)
    print(category)
    if request.method == 'POST':
        category.delete()
        return redirect('dashboard:addcategory')  # Replace 'category_list' with the URL name of your category list view
    return redirect('dashboard:addcategory')
    
def edit_tags(request, tag_id):
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

def delete_tags(request, tag_id):
    print("reachedd delete")
    tag = get_object_or_404(Product_Tags, id=tag_id)

    if request.method == 'POST':
        tag.delete()
        return redirect('dashboard:addtags')  # Replace 'category_list' with the URL name of your category list view
    return redirect('dashboard:addtags')


def delete_product(request, id):
    try:
        product = Products_Table.objects.get(id=id)
        product.delete()
        messages.success(request, "Product deleted successfully.")
    except product.DoesNotExist:
        messages.error(request, "Product does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('dashboard:products')



def status(request, id):
    try:
        product = Products_Table.objects.get(id=id)
        if product.is_active:
            product.is_active = False
            print("y")
            
        else:
            product.is_active = True
            print("yeee")
        
        product.save()
         
        messages.success(request, "Product status changed.")
    except product.DoesNotExist:
        messages.error(request, "Product does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('dashboard:products')

def productdetails(request,id):
    product = Products_Table.objects.get(id = id)
    variations = Product_item.objects.filter(product = product)
    images = Product_images.objects.filter(product = product)
    context = {
         'product':product,
         'variations' : variations,
         'images' : images,

     }

    return render(request, 'dashboard/page-seller-detail.html',context)


def pro(request):
    products = Products_Table.objects.all()
    context = {
         'products':products,
     }

    return render(request, 'dashboard/allproducts.html',context)


def deleteimage(request,id,image_id):
    product = Products_Table.objects.get(id = id)
    image = Product_images.objects.get(product = product , id = image_id)
    image.delete()
    referring_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(referring_page)


def upload_image(request,id):
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

def changethumbnail(request,id):
    if request.method == 'POST':
        image_data = request.POST.get('image')
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')

        try:
            product = Products_Table.objects.get(id = id)
            product.image = image_file
            product.save()
        except IntegrityError:
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

def users(request):
    users = User_Accounts.objects.filter(is_superuser=False).order_by('id').reverse()
    context = {
        'users': users,
    }
    return render(request,'dashboard/users.html',context)

def userdetails(request,id):
    user = User_Accounts.objects.get(id = id)
    # context = {
    #     'user' : user,
    # }
    # return render(request,'dashboard/userdetails.html',context)
    return HttpResponse(user.username)
    
