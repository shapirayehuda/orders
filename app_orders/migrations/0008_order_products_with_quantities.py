# Generated by Django 4.0.2 on 2023-07-30 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_orders', '0007_remove_order_orderer_name_remove_order_phone_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='products_with_quantities',
            field=models.TextField(blank=True, null=True),
        ),
    ]
