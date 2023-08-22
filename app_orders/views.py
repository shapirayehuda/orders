# views.py

from django.shortcuts import render, redirect, HttpResponse
from .models import Product, Order, Orderer, OrderItem
from django.db.models import Count
from datetime import date, timedelta, datetime
import json

# views.py

def orderer_list(request):
    orderer_list = Orderer.objects.all()
    return render(request, 'orderer_list.html', {'orderer_list': orderer_list})


# views.py

def available_products(request):
    unique_products = Product.objects.values('Product_name').annotate(count=Count('Product_name')).filter(count__gt=0)
    orders = Order.objects.all().order_by('-start_date').prefetch_related('items__product')

    selected_date = request.GET.get('selected_date')
    if selected_date:
        try:
            selected_date = date.fromisoformat(selected_date)
        except ValueError:
            selected_date = None

    # Get all unique dates until the end of the year
    all_dates = [date.today() + timedelta(days=i) for i in range(365)]

    # Create a dictionary to store available products for each date
    available_products_by_date = {current_date: [] for current_date in all_dates}

    for current_date in all_dates:
        # Get all orders within the current date range
        orders_in_date_range = orders.filter(start_date__lte=current_date, end_date__gte=current_date)

        # Create a dictionary to store the total ordered quantity for each product
        total_ordered_quantity = {product['Product_name']: 0 for product in unique_products}

        # Calculate the total ordered quantity for each product on the current date
        for order in orders_in_date_range:
            for item in order.items.all():
                total_ordered_quantity[item.product.Product_name] += item.quantity

        # Calculate the available products for the current date
        available_products = [
            {
                'Product_name': product['Product_name'],
                'quantity': product['count'] - total_ordered_quantity[product['Product_name']],
            }
            for product in unique_products
            if product['count'] - total_ordered_quantity[product['Product_name']] > 0
        ]

        # Add the available products for the current date to the dictionary
        available_products_by_date[current_date] = available_products  

    return render(request, 'available_products.html', {
        'selected_date': selected_date,
        'available_products_by_date': available_products_by_date,
    })


# views.py

def create_order(request):
    if request.method == 'POST':
        orderer_name = request.POST.get('orderer_name')
        phone_number = request.POST.get('phone_number')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        selected_products = request.POST.getlist('products[]')
        products_with_quantities = {
            product_name: int(request.POST.get(f"{product_name}_quantity", 0))
            for product_name in selected_products
        }

        # Convert products_with_quantities dictionary to a JSON string
        products_with_quantities_json = json.dumps(products_with_quantities)

        # Store the selected products and quantities in the session
        request.session['selected_products'] = selected_products
        request.session['products_with_quantities'] = products_with_quantities_json

        # Get the first Orderer object with the same name and phone number
        orderer = Orderer.objects.filter(orderer_name=orderer_name, phone_number=phone_number).first()

        # If no matching Orderer is found, create a new one
        if not orderer:
            orderer = Orderer.objects.create(orderer_name=orderer_name, phone_number=phone_number)

        # Create Order object
        order = Order.objects.create(
            orderer=orderer, 
            start_date=start_date,
            end_date=end_date,
            products_with_quantities=products_with_quantities_json
        )

        for product_name in selected_products:
            quantity = products_with_quantities.get(product_name, 0)

            if quantity > 0:
                # Use filter() to handle MultipleObjectsReturned situation
                products = Product.objects.filter(Product_name=product_name)

                if products.exists():
                    product = products.first()
                    order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity)
                    
        return redirect('order_list')

    today = date.today().isoformat()
    default_end_date = (date.today() + timedelta(days=5)).isoformat()
    start_date = request.POST.get('start_date', today)
    unique_products = Product.objects.values('Product_name').annotate(count=Count('Product_name')).filter(count__gt=0)

    return render(request, 'create_order.html', {'products': unique_products, 'today': today, 'default_end_date': default_end_date})

			
# views.py

def order_list(request):
    # Retrieve the selected products and quantities from the session
    selected_products = request.session.get('selected_products', [])
    products_with_quantities_json = request.session.get('products_with_quantities')

    # Parse the JSON string to a dictionary
    products_with_quantities = json.loads(products_with_quantities_json) if products_with_quantities_json else {}

    orders = Order.objects.all().order_by('-start_date').prefetch_related('items__product')

    for order in orders:
        # Load the products_with_quantities JSON string back into a dictionary for each order
        order_products_with_quantities_json = order.products_with_quantities
        order_products_with_quantities = json.loads(order_products_with_quantities_json) if order_products_with_quantities_json else {}
        order.products_with_quantities = order_products_with_quantities

    return render(request, 'order_list.html', {'orders': orders, 'selected_products': selected_products, 'products_with_quantities': products_with_quantities})


# views.py

def product_list(request):

    products = Product.objects.all()
    unique_products = Product.objects.values('Product_name').annotate(count=Count('Product_name')).filter(count__gt=0)
    
    return render(request, 'product_list.html', {'products': unique_products })


# views.py  
  
def index(request):
    today = date.today().isoformat()
    unique_products = Product.objects.values('Product_name').annotate(count=Count('Product_name')).filter(count__gt=0)
    orders = Order.objects.all().order_by('-start_date').prefetch_related('items__product')

    selected_date = request.GET.get('selected_date')
    if selected_date:
        try:
            selected_date = date.fromisoformat(selected_date)
        except ValueError:
            selected_date = None
    else:
        selected_date = None

    # Get all unique dates until the end of the year
    all_dates = [date.today() + timedelta(days=i) for i in range(365)]

    # Create a dictionary to store available products for each date
    available_products_by_date = {current_date: [] for current_date in all_dates}

    available_products = available_products_by_date.get(selected_date, [])

    for current_date in all_dates:
        # Get all orders within the current date range
        orders_in_date_range = orders.filter(start_date__lte=current_date, end_date__gte=current_date)

        # Create a dictionary to store the total ordered quantity for each product
        total_ordered_quantity = {product['Product_name']: 0 for product in unique_products}

        # Calculate the total ordered quantity for each product on the current date
        for order in orders_in_date_range:
            for item in order.items.all():
                total_ordered_quantity[item.product.Product_name] += item.quantity

        # Calculate the available products for the current date
        available_products = [
            {
                'Product_name': product['Product_name'],
                'quantity': product['count'] - total_ordered_quantity[product['Product_name']],
            }
            for product in unique_products
            if product['count'] - total_ordered_quantity[product['Product_name']] > 0
        ]

        # Add the available products for the current date to the dictionary
        available_products_by_date[current_date] = available_products

    if selected_date:
        default_end_date = (selected_date + timedelta(days=5)).isoformat()
    else:
        default_end_date = (date.today() + timedelta(days=5)).isoformat()

    start_date = request.POST.get('start_date', today)

        
    # ... (create_order view logic)
    if request.method == 'POST':
        orderer_name = request.POST.get('orderer_name')
        phone_number = request.POST.get('phone_number')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        selected_products = request.POST.getlist('products[]')
        products_with_quantities = {
            product_name: int(request.POST.get(f"{product_name}_quantity", 0))
            for product_name in selected_products
        }

        # Convert products_with_quantities dictionary to a JSON string
        products_with_quantities_json = json.dumps(products_with_quantities)

        # Store the selected products and quantities in the session
        request.session['selected_products'] = selected_products
        request.session['products_with_quantities'] = products_with_quantities_json

        # Get the first Orderer object with the same name and phone number
        orderer = Orderer.objects.filter(orderer_name=orderer_name, phone_number=phone_number).first()

        # If no matching Orderer is found, create a new one
        if not orderer:
            orderer = Orderer.objects.create(orderer_name=orderer_name, phone_number=phone_number)

        # Create Order object
        order = Order.objects.create(
            orderer=orderer, 
            start_date=start_date,
            end_date=end_date,
            products_with_quantities=products_with_quantities_json
        )

        for product_name in selected_products:
            quantity = products_with_quantities.get(product_name, 0)

            if quantity > 0:
                # Use filter() to handle MultipleObjectsReturned situation
                products = Product.objects.filter(Product_name=product_name)

                if products.exists():
                    product = products.first()
                    order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity)
                    
        return redirect('order_list')

    return render(request, 'index.html', {
        'products': unique_products,
        'selected_date': selected_date,
        'available_products_by_date': available_products_by_date,
        'today': today,
        'default_end_date': default_end_date,
       
    })