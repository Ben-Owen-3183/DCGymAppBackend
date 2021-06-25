# Generated by Django 3.1.7 on 2021-06-21 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentreplies',
            name='like_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='like_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='pinned',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='pinned_time_days',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='pinned_timed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='postcomment',
            name='like_count',
            field=models.IntegerField(default=0),
        ),
    ]
