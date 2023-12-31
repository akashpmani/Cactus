# Generated by Django 4.2.1 on 2023-05-16 12:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Category_name', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(max_length=255, null=True, unique=True)),
                ('is_child', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='products.category')),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Product_Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('color_code', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Colors',
            },
        ),
        migrations.CreateModel(
            name='Product_Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(max_length=255, null=True, unique=True)),
            ],
            options={
                'verbose_name': 'product tag',
                'verbose_name_plural': ' Product Tags',
            },
        ),
        migrations.CreateModel(
            name='Products_Table',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('slug', models.SlugField(max_length=255, null=True, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('bio_name', models.CharField(max_length=255, null=True)),
                ('description', models.TextField()),
                ('care_instruction', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('sku', models.CharField(max_length=100, null=True, unique=True)),
                ('category', models.ForeignKey(blank=True, limit_choices_to={'is_child': True}, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.category')),
            ],
        ),
        migrations.CreateModel(
            name='Product_item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=55)),
                ('size', models.CharField(choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large')], max_length=255)),
                ('price', models.PositiveIntegerField(default=0)),
                ('images', models.ImageField(null=True, upload_to='products/')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.products_table')),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='Product_images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to='products/')),
                ('featured', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product_item')),
            ],
        ),
        migrations.CreateModel(
            name='ProductTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.products_table')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product_tags')),
            ],
            options={
                'unique_together': {('product', 'tag')},
            },
        ),
    ]
