# Generated by Django 4.2.1 on 2023-06-23 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_alter_product_item_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classfiedproducts',
            name='offer',
        ),
    ]
