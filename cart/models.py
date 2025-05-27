from django.db import models
from decimal import Decimal
from django.utils import timezone
import uuid
from store.models import Product
from django.contrib.postgres.fields import JSONField

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)  # Track updates

    def save(self, *args, **kwargs):
        if not self.cart_id:
            self.cart_id = str(uuid.uuid4())
        super().save(*args, **kwargs)


"""
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    customizations = models.JSONField(blank=True, null=True) # Store all customization options
    
    def __str__(self):
        return self.product
    
"""    

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    #  Holds selected variation options (like lapel, vent, monogram etc.)
    selected_options = models.JSONField(default=dict, blank=True)

    #  If you want to separate other metadata or text inputs (e.g., monogram text, initials)
    customizations = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def calculate_total_price(self):
        extra_price = 0
        for option_data in self.selected_options.values():
            try:
                extra_price += float(option_data.get("price_difference", 0))
            except (TypeError, ValueError):
                continue
        return (self.base_price + extra_price) * self.quantity




# Free shipping threshold and gift wrap price fixing
class CartSettings(models.Model):
    free_shipping_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('300.00')
    )
    gift_wrap_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('5.00')
    )

    def __str__(self):
        return f"Cart Settings (Free shipping over ${self.free_shipping_threshold}, Gift wrap ${self.gift_wrap_price})"

    class Meta:
        verbose_name = "Cart Setting"
        verbose_name_plural = "Cart Settings"
