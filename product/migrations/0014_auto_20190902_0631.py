# Generated by Django 2.2.4 on 2019-09-02 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_cart_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart', to='product.Color'),
        ),
    ]