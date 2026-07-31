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

def create_payment_intent_for_item(item_id):
    item = Item.objects.get(id=item_id)
    secret_key, _ = get_stripe_keys(item.currency)
    stripe.api_key = secret_key
    
    intent = stripe.PaymentIntent.create(
        amount=item.price,
        currency=item.currency,
        metadata={'item_id': item.id},
        automatic_payment_methods={'enabled': True},
    )
    return intent.client_secret

def create_payment_intent_for_order(order_id):
    order = Order.objects.get(id=order_id)
    main_currency = order.items.first().currency
    secret_key, _ = get_stripe_keys(main_currency)
    stripe.api_key = secret_key
    
    intent = stripe.PaymentIntent.create(
        amount=order.get_total(),
        currency=main_currency,
        metadata={'order_id': order.id},
        automatic_payment_methods={'enabled': True},
    )

    order.payment_intent_id = intent.id
    order.save(update_fields=['payment_intent_id'])
    
    return intent.client_secret