# Generated by Django 3.1.7 on 2021-08-07 14:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=150, unique=True)),
                ('customer', models.CharField(max_length=150)),
                ('mandate', models.CharField(max_length=150)),
                ('subscription', models.CharField(max_length=150)),
                ('active', models.BooleanField()),
                ('api_type', models.CharField(choices=[('stripe', 'Stripe'), ('go_cardless', 'Go Cardless')], default='stripe', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='PasswordResets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=150)),
                ('email', models.CharField(max_length=150)),
                ('v_token', models.CharField(max_length=150)),
                ('timestamp', models.DateField()),
                ('locked', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='UserAvatar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_name', models.CharField(max_length=150)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
