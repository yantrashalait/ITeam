# Generated by Django 2.2.6 on 2020-01-16 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_auto_20191001_0528'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutiteam',
            name='address',
            field=models.CharField(default='', max_length=255),
        ),
    ]
