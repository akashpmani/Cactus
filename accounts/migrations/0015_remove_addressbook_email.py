# Generated by Django 4.2.1 on 2023-06-12 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_rename_city_state_rename_country_state_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addressbook',
            name='email',
        ),
    ]
