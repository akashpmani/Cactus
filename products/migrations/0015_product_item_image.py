# Generated by Django 4.2.1 on 2023-06-20 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_product_item_slug_alter_products_table_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
