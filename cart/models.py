from django.db import models

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
    
    