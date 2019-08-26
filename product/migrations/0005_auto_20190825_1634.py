# Generated by Django 2.2.4 on 2019-08-25 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_auto_20190824_0528'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='Is this product available in stock?',
        ),
        migrations.AddField(
            model_name='product',
            name='availability',
            field=models.BooleanField(default=False, verbose_name='Is this product available in stock?'),
        ),
    ]
