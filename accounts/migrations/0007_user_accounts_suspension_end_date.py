# Generated by Django 4.2.1 on 2023-05-15 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_user_accounts_otp_verified_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_accounts',
            name='suspension_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
