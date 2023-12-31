# Generated by Django 4.0.2 on 2023-07-24 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_orders', '0006_alter_orderitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='orderer_name',
        ),
        migrations.RemoveField(
            model_name='order',
            name='phone_number',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app_orders.order'),
        ),
    ]
