import stripe
from django.conf import settings
from .models import Item, Order

currency_keys = {
    'eur': (settings.STRIPE_SECRET_KEY_EUR, settings.STRIPE_PUBLISHABLE_KEY_EUR),
    'usd': (settings.STRIPE_SECRET_KEY_USD, settings.STRIPE_PUBLISHABLE_KEY_USD)
}

def get_stripe_keys(currency):
    if currency in currency_keys.keys():
        return currency_keys[currency]
    else:
        raise ValueError("Currency is unknown")

def create_checkout_session_for_item(item_id):
    item = Item.objects.get(id=item_id)
    secret_key, _ = get_stripe_keys(item.currency)
    stripe.api_key = secret_key
    
    success_url = f'http://{settings.BASE_URL}/success/'
    cancel_url = f'http://{settings.BASE_URL}/item/{item.id}/'
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': item.currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': item.price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={'item_id': item.id},
    )
    return session.id

def create_checkout_session_for_order(order_id):
    order = Order.objects.get(id=order_id)
    main_currency = order.items.first().currency
    secret_key, _ = get_stripe_keys(main_currency)
    stripe.api_key = secret_key
    
    line_items = []
    discounts = []
    tax_rates = []

    for item in order.items.all():
        if item.currency != main_currency:
            raise ValueError("All items must have the same currency")
        line_items.append({
            'price_data': {
                'currency': main_currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': item.price,
            },
            'quantity': 1,
        })
    
    if order.discount:
        if order.discount.percent_off:
            discounts.append({
                'coupon': order.discount.stripe_coupon_id
            })
    
    if order.tax:
        tax_rates.append(order.tax.stripe_tax_rate_id)
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=f'http://{settings.BASE_URL}/success/',
        cancel_url=f'http://{settings.BASE_URL}/order/{order.id}/',
        discounts=discounts if discounts else None,
        tax_rates=tax_rates if tax_rates else None,
        metadata={'order_id': order.id},
    )
    return session.id