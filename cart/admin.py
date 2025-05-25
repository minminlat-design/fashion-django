from django.contrib import admin
from .models import Cart, CartItem, CartSettings


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'date_added']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'is_active']
    
    


@admin.register(CartSettings)
class CartSettingsAdmin(admin.ModelAdmin):
    list_display = ('free_shipping_threshold', 'gift_wrap_price')

