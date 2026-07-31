from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class Currency(models.TextChoices):
    USD = 'usd', 'US Dollar'
    EUR = 'eur', 'Euro'

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(help_text="Price in cents (e.g., 1000 = 10.00)")
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)

    def __str__(self):
        return self.name

    def display_price(self):
        return f"{self.price/100:.2f} {self.currency.upper()}"

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    stripe_tax_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

class Discount(models.Model):
    name = models.CharField(max_length=100)
    percent_off = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    amount_off = models.IntegerField(null=True, blank=True)  # in cents
    currency = models.CharField(max_length=3, choices=Currency.choices, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    items = models.ManyToManyField(Item)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.IntegerField(default=0, help_text="Price in cents (e.g., 1000 = 10.00)")
    created_at = models.DateTimeField(auto_now_add=True)

    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    stripe_payment_status = models.CharField(max_length=50, blank=True, null=True)

    def update_total(self):
        items_sum = sum([item.price for item in self.items.all()])
        self.total_price = items_sum
        self.save(update_fields=['total_price'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_total(self):
        total = self.total_price
        if self.discount:
            if self.discount.percent_off:
                total = total * (1 - self.discount.percent_off / 100)
            elif self.discount.amount_off:
                total -= self.discount.amount_off
        if self.tax:
            total += total * (self.tax.percentage / 100)
        return int(total)

    def __str__(self):
        return f"Order #{self.id} - {self.created_at}"
    

@receiver(m2m_changed, sender=Order.items.through)
def update_order_total(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.update_total()