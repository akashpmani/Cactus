# Generated by Django 4.2.1 on 2023-06-21 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_product_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_item',
            name='slug',
            field=models.SlugField(blank=True, max_length=255),
        ),
    ]
