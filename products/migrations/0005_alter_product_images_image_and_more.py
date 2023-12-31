# Generated by Django 4.2.1 on 2023-05-23 20:14

from django.db import migrations, models
import django.db.models.deletion
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_product_item_color_remove_product_item_images_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_images',
            name='image',
            field=models.ImageField(null=True, upload_to=products.models.upload_path),
        ),
        migrations.AlterField(
            model_name='product_images',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.products_table'),
        ),
    ]
