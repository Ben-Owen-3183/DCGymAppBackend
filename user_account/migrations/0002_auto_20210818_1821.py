# Generated by Django 3.1.7 on 2021-08-18 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membershipstatus',
            old_name='customer',
            new_name='customer_id',
        ),
        migrations.RenameField(
            model_name='membershipstatus',
            old_name='mandate',
            new_name='mandate_id',
        ),
        migrations.RenameField(
            model_name='membershipstatus',
            old_name='subscription',
            new_name='subscription_id',
        ),
    ]
