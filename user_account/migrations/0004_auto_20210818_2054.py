# Generated by Django 3.1.7 on 2021-08-18 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0003_auto_20210818_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipstatus',
            name='customer_id',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
