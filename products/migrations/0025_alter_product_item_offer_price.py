# Generated by Django 4.2.1 on 2023-06-23 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_alter_product_item_offer_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_item',
            name='offer_price',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
