from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Item, Order
from .services import get_stripe_keys, create_payment_intent_for_item, create_payment_intent_for_order

def item_detail(request, id):
    item = get_object_or_404(Item, id=id)
    _, public_key = get_stripe_keys(item.currency)
    
    return render(request, 'payment/item_detail.html', {
        'item': item,
        'stripe_pub_key': public_key,
    })

@csrf_exempt
def buy_item(request, id):
    if request.method == 'GET':
        try:
            client_secret = create_payment_intent_for_item(id)
            return JsonResponse({'clientSecret': client_secret})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    first_item = order.items.first()
    _, public_key = get_stripe_keys(first_item.currency) if first_item else (None, None)
    
    return render(request, 'payment/order_detail.html', {
        'order': order,
        'stripe_pub_key': public_key,
        'total': order.get_total() / 100 if order.get_total() else 0,
    })

@csrf_exempt
def buy_order(request, id):
    if request.method == 'GET':
        try:
            client_secret = create_payment_intent_for_order(id)
            return JsonResponse({'clientSecret': client_secret})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def success_page(request):
    return render(request, 'payment/success.html')