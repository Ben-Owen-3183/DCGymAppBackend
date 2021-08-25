# Generated by Django 3.1.7 on 2021-08-21 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0004_auto_20210818_2054'),
    ]

    operations = [
        migrations.CreateModel(
            name='PairedAccounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_account.membershipstatus')),
            ],
        ),
    ]
