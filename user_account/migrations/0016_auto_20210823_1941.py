# Generated by Django 3.1.7 on 2021-08-23 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0015_auto_20210823_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipstatus',
            name='api_type',
            field=models.CharField(choices=[('stripe', 'Stripe'), ('go_cardless', 'Go Cardless'), ('manual', 'Manual')], default='stripe', max_length=20),
        ),
    ]