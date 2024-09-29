from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
import random
from datetime import timedelta, datetime

# Create your views here.

DAILY_MENU = {
    'Quantum Quiche Lorraine': 11.49,
    'AI-Enhanced Avocado Toast': 9.99,
    'Smart Smashed Burger': 14.49,
    'Augmented Reality Ribs': 17.99,
    'Algorithmic Apple Pie': 7.99,
}

DAILY_SPECIALS = [
    {'name': 'Predictive Pasta Carbonara', 'price': 13.99},
    {'name': 'Neural Nacho Nirvana', 'price': 11.99},
    {'name': 'Deep-Learned Dumplings', 'price': 12.99},
    {'name': 'Cyber-Crunchy Chicken Tenders', 'price': 10.99}
]




def main_page(request):
    return render(request, 'restaurant/main.html', {
        'name': 'Flying Stone Canteen',
        'location': '9071 High Noon Street, Panama City, FL',
        'hours': [
            {'day': 'Monday - Friday', 'hours': '10 AM - 9 PM'},
            {'day': 'Saturday', 'hours': '12 PM - 10 PM'},
            {'day': 'Sunday', 'hours': 'Closed'}
        ],
        'photos': ['images/output.jpg'] 
    })


def order_page(request):
    daily_special = random.choice(DAILY_SPECIALS)

    # pass the menu and daily special to the template
    return render(request, 'restaurant/order.html', {
        'menu_items': DAILY_MENU,
        'daily_special': daily_special 
    })

def confirmation_page(request):
    # Check if the request method is POST and contains order details
    if request.method == "POST":
        ordered_items = request.POST.getlist('menu_items')
        customer_name = request.POST.get('name', 'Customer')  # Default to 'Customer' if not provided

        total_price = sum(DAILY_MENU[item] for item in ordered_items if item in DAILY_MENU)

        ready_time = timezone.localtime(timezone.now() + timedelta(minutes=random.randint(30, 60)))

        # pass the ordered items, customer info, total price, and ready time to the template
        return render(request, 'restaurant/confirmation.html', {
            'ordered_items': ordered_items,
            'total_price': total_price,
            'customer_name': customer_name,
            'ready_time': ready_time
        })
    
    # If the request method is not POST, redirect to the order page
    return redirect('order') 


