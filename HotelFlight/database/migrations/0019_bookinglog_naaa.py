# Generated by Django 2.2.2 on 2019-09-04 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0018_auto_20190903_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinglog',
            name='naaa',
            field=models.IntegerField(default=1),
        ),
    ]