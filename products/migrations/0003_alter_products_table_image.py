# Generated by Django 4.2.1 on 2023-05-22 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_products_table_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products_table',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='upload_to=generate_upload_path)'),
        ),
    ]
