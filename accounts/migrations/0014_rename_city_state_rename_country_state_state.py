# Generated by Django 4.2.1 on 2023-06-11 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_country_city'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='City',
            new_name='State',
        ),
        migrations.RenameField(
            model_name='state',
            old_name='country',
            new_name='State',
        ),
    ]
