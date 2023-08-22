from django.contrib import admin

# Register your models here.
from .models import Orderer, Product, Order

# Register your models here.
admin.site.register(Orderer)
admin.site.register(Product)
admin.site.register(Order)