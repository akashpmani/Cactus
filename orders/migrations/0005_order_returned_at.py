# Generated by Django 4.2.1 on 2023-07-28 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='returned_at',
            field=models.DateTimeField(null=True),
        ),
    ]
