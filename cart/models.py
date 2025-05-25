from django.db import models
from decimal import Decimal

from store.models import Product
from django.contrib.postgres.fields import JSONField

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    customizations = models.JSONField(blank=True, null=True) # Store all customization options
    
    def __str__(self):
        return self.product
    
    


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
