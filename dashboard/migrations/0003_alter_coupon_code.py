# Generated by Django 4.2.1 on 2023-07-22 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_coupon_max_discount_alter_coupon_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
