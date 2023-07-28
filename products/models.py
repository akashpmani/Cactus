from datetime import timezone
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from datetime import timezone
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User


# Create your models here.


# category model , Added boolean field to indicate if it's a child category
class Category(models.Model):
    category_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    is_child = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("store:category_list", args=[self.slug])

    def __str__(self):
        return self.category_name

# tag for sorting the products fast


class Product_Tags(models.Model):

    tag_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = "product tag"
        verbose_name_plural = " Product Tags"

    def __str__(self):
        return self.tag_name


# Color
class Product_Color(models.Model):
    title = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Colors'

    def __str__(self):
        return self.title

def generate_upload_path(instance, filename):
    # Get the name of the product
    product_name = instance.name
    # Generate the upload path using the product name
    upload_path = f'products/{product_name}/{filename}'
    return upload_path

# basic table that describes about product
class Products_Table(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=255, unique=True, null=False)
    # Using limit_choices_to to filter out parent categories , only categories with is_child=True will be here
    category = models.ForeignKey(Category, null=True, blank=True,
                                 on_delete=models.CASCADE, limit_choices_to={'is_child': True})
    name = models.CharField(max_length=255)
    bio_name = models.CharField(max_length=255, null=True)
    description = models.TextField()
    care_instruction = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=generate_upload_path)
    sku = models.CharField(max_length=100, unique=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product.title

    def save(self, *args, **kwargs):
        # Generate and set SKU before saving the instance
        if not self.sku:
            # Generate SKU from product name, category, size, color using slugify
            category_name = self.category.category_name
            sku = f'{slugify(category_name)}-{slugify(self.name)}'
            self.sku = sku

        super(Products_Table, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class P_tags(models.Model):
    product = models.ForeignKey(Products_Table, on_delete=models.CASCADE, related_name='p_tags_set')
    tag = models.ForeignKey(Product_Tags, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'tag')

    def __str__(self):
        return f'{self.product} - {self.tag}'


# table for keeping the data of variations
class Product_item(models.Model):
    product = models.ForeignKey(Products_Table, on_delete=models.CASCADE)
    #size variations sizes are predefined
    SIZE_CHOICES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    )
    size = models.CharField(max_length=255,
                            choices=SIZE_CHOICES)
    price = models.PositiveIntegerField(default=0)
    offer_price = models.PositiveIntegerField(null=True,default=0)
    quantity = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, blank=True)
    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Products_varients'
        unique_together = ('product', 'size')
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.product.slug
        super(Product_item, self).save(*args, **kwargs)
        if not self.image:
            self.image = self.product.image
        super(Product_item, self).save(*args, **kwargs)
        if self.offer_price == 0:
            self.offer_price = self.price
        super(Product_item, self).save(*args, **kwargs)
        
        
    def __str__(self):
        return f"{self.product.name}, {self.get_size_display()}"

def upload_path(instance, filename):
    # Get the name of the product
    print('product_name')
    product_name = instance.product.name
    print(product_name)
    # Generate the upload path using the product name
    upload_path = f'products/{product_name}/{filename}'
    return upload_path


# additional image field for adding extra images of the product according to variations
class Product_images(models.Model):
    product = models.ForeignKey(Products_Table, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_path, null=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
         return self.product.name
     
class ProductClassification(models.Model):
    title = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='product_photos/')

    def __str__(self):
        return self.title
    
class classfiedProducts(models.Model):
    classification = models.ForeignKey(ProductClassification, on_delete=models.CASCADE)
    product = models.ForeignKey(Products_Table, on_delete=models.CASCADE)
    offer = models.PositiveIntegerField(null=True , default=True)
    
    class Meta:
        unique_together = ('product', 'classification')

    def __str__(self):
        return f'{self.product} - {self.classification}'
    def save(self, *args, **kwargs):
        product_item = Product_item.objects.filter(product = self.product)
        for item in product_item:
            price = item.price
            reduced_price =price - (price * self.offer / 100)
            item.offer_price = reduced_price
            item.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        product_item = Product_item.objects.filter(product = self.product)
        for item in product_item:
            item.offer_price = None
            item.save()
        
        super().delete(*args, **kwargs)