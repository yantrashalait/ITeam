# Generated by Django 2.2.4 on 2019-09-06 06:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0021_merge_20190904_0753'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userrequestproduct',
            name='user',
        ),
    ]
