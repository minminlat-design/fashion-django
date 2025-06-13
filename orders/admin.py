from django.contrib import admin
from .models import Order, OrderItem
from django.utils.safestring import mark_safe


def order_payment(obj):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ''

order_payment.short_description = 'Stripe Payment'



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = (
        'product', 'product_name', 'quantity',
        'base_price', 'total_price',
        'gift_wrap', 'user_measurement',
        'frozen_measurement_data',
        'selected_options', 'customizations'
    )
    can_delete = False
    extra = 0  # No empty extra forms

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'paid', 'status', 'total_price', order_payment)
    list_filter = ('paid', 'status', 'created')
    search_fields = ('id', 'user__email', 'email', 'first_name', 'last_name')
    readonly_fields = (
        'user', 'first_name', 'last_name', 'email',
        'phone', 'country',
        'address', 'postal_code', 'city',
        'created', 'updated', 'total_price'
    )
    inlines = [OrderItemInline]

    fieldsets = (
        ('Customer Info', {
            'fields': (
                'user', 'first_name', 'last_name', 'email', 'phone'
            )
        }),
        ('Shipping Info', {
            'fields': (
                'address', 'postal_code', 'city', 'country'
            )
        }),
        ('Status & Metadata', {
            'fields': (
                'paid', 'status', 'total_price', 'created', 'updated'
            )
        }),
    )
