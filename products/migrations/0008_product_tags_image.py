# Generated by Django 4.2.1 on 2023-06-12 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_rename_category_name_category_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_tags',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
