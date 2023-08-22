# models.py

from django.db import models
from datetime import date, timedelta
import json

class Orderer(models.Model):
    orderer_id = models.AutoField(primary_key=True)
    orderer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

class Product(models.Model):
    Product_id = models.AutoField(primary_key=True)
    Product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    
    def quantity_ordered_for_date(self, start_date, end_date):
        # Get the total quantity of this product ordered between start_date and end_date
        ordered_items = OrderItem.objects.filter(
            product=self,
            order__start_date__lte=end_date,
            order__end_date__gte=start_date,
        )
        total_quantity = ordered_items.aggregate(models.Sum('quantity'))['quantity__sum']
        return total_quantity or 0

class Order(models.Model):
    orderer = models.ForeignKey(Orderer, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    products = models.ManyToManyField(Product)
    products_with_quantities = models.JSONField(default=dict)
    
    def get_available_products_by_date(self):
        # Get all products related to this order
        products = self.products.all()

        # Get the ordered quantities for each product in this order
        ordered_quantities = {
            item.product.Product_name: item.quantity
            for item in self.items.all()
        }

        # Calculate the available products for this order's date range
        available_products = [
            {
                'Product_name': product.Product_name,
                'quantity': product.quantity - ordered_quantities.get(product.Product_name, 0)
            }
            for product in products
            if product.quantity - ordered_quantities.get(product.Product_name, 0) > 0
        ]

        return available_products
   
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Update the related_name
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
        
    def __str__(self):
        return f"{self.product.Product_name} - {self.quantity}"
    
   
    