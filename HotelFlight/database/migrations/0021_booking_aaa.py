# Generated by Django 2.2.2 on 2019-09-04 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0020_remove_bookinglog_naaa'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='aaa',
            field=models.IntegerField(default=0),
        ),
    ]
