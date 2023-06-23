# Generated by Django 4.2.1 on 2023-06-20 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_classfiedproducts'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_item',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='products_table',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]
