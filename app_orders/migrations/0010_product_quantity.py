# Generated by Django 4.0.2 on 2023-07-30 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_orders', '0009_alter_order_products_with_quantities'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
