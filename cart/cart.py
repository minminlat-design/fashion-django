from decimal import Decimal
from django.conf import settings
from store.models import Product
from .models import CartSettings


def get_cart_settings():
    try:
        return CartSettings.objects.latest('id')
    except CartSettings.DoesNotExist:
        # Return default values if no settings exist
        return CartSettings(free_shipping_threshold=Decimal('300.00'), gift_wrap_price=Decimal('5.00'))


class Cart:
    FREE_SHIPPING_THRESHOLD = Decimal('300.00')
    
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
            
        self.cart = cart
        
        # Load settings dynamically
        settings_obj = get_cart_settings()

        self.FREE_SHIPPING_THRESHOLD = settings_obj.free_shipping_threshold
        self.gift_wrap_price = settings_obj.gift_wrap_price
        self.gift_wrap = self.cart.get('gift_wrap', False)
        
        

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        price = str(product.discounted_price if product.discounted_price else product.price)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': price
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        # Save cart and gift_wrap separately in session
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session['gift_wrap'] = self.gift_wrap
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        # Get only product IDs that are digits (exclude other keys)
        product_ids = [key for key in self.cart.keys() if key.isdigit()]

        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            if isinstance(item, dict) and 'price' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for key, item in self.cart.items() if key.isdigit())

    def get_total_price(self):
        total = sum(
            Decimal(item['price']) * item['quantity']
            for key, item in self.cart.items()
            if key.isdigit() and isinstance(item, dict) and 'price' in item
        )
        if self.gift_wrap:
            total += self.gift_wrap_price
        return total

    def clear(self):
        # remove cart and gift_wrap from session
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        if 'gift_wrap' in self.session:
            del self.session['gift_wrap']
        self.session.modified = True

    def get_free_shipping_data(self):
        total = self.get_total_price()
        qualified = total >= self.FREE_SHIPPING_THRESHOLD
        remaining = max(self.FREE_SHIPPING_THRESHOLD - total, Decimal('0.00'))

        if self.FREE_SHIPPING_THRESHOLD > 0:
            raw_progress = float(total / self.FREE_SHIPPING_THRESHOLD)
            progress = min(raw_progress, 1.0)  # clamp to 1.0
        else:
            progress = 0.0

        return {
            'progress': progress,  # e.g. 0.25 for 25%
            'remaining': remaining,
            'qualified': qualified
        }

    def update(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.save()

    def get_item_total(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            quantity = self.cart[product_id]['quantity']
            price = Decimal(self.cart[product_id]['price'])
            return float(price * quantity)
        return 0.0

    def toggle_gift_wrap(self, enable: bool):
        self.gift_wrap = enable
        self.save()
