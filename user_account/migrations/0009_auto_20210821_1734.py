# Generated by Django 3.1.7 on 2021-08-21 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0008_auto_20210821_1730'),
    ]

    operations = [
        migrations.RenameField(
            model_name='linkedacount',
            old_name='linked_account',
            new_name='child_account',
        ),
        migrations.RenameField(
            model_name='linkedacount',
            old_name='main_joint_account',
            new_name='parent_account',
        ),
    ]
