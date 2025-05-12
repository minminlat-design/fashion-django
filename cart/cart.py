from decimal import Decimal
from django.conf import settings
from store.models import Product

# Fix: Use Decimal instead of float
GIFT_WRAP_PRICE = Decimal("5.00")
SHIPPING_COST = Decimal("10.00")
FREE_SHIPPING_THRESHOLD = Decimal("100.00")

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = [int(k) for k in self.cart.keys() if k.isdigit()]
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for product_id in product_ids:
            item = cart[str(product_id)]
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(
            self.cart[key]['quantity']
            for key in self.cart
            if key.isdigit() and 'quantity' in self.cart[key]
        )

    def get_gift_wrap_price(self):
        return GIFT_WRAP_PRICE if self.cart.get('gift_wrap', False) else Decimal("0.00")

    def get_shipping_price(self, subtotal):
        if self.cart.get('free_shipping', False) or subtotal >= FREE_SHIPPING_THRESHOLD:
            return Decimal("0.00")
        return SHIPPING_COST

    def get_total_price(self):
        subtotal = sum(
            Decimal(item['price']) * item['quantity']
            for key in self.cart
            if key.isdigit() and 'price' in self.cart[key]
            for item in [self.cart[key]]
        )
        total = subtotal + self.get_gift_wrap_price() + self.get_shipping_price(subtotal)
        return total

    def clear(self):
        # Remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()
