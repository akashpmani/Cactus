# Generated by Django 4.2.1 on 2023-07-31 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_rename_apply_coupon_verify_coupon'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarouselItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/')),
                ('sub_text', models.CharField(max_length=100, null=True)),
                ('about', models.CharField(max_length=100, null=True)),
                ('main_text', models.CharField(max_length=100, null=True)),
                ('main_text_1', models.CharField(max_length=100, null=True)),
                ('link', models.URLField(null=True)),
            ],
        ),
    ]
