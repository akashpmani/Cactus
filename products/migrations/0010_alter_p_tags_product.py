# Generated by Django 4.2.1 on 2023-06-12 20:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_rename_producttag_p_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='p_tags',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_tags_set', to='products.products_table'),
        ),
    ]
