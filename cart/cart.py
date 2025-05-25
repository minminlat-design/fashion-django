from decimal import Decimal
from django.conf import settings
from store.models import Product



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
        
        self.session.modified = True

        
        
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
           
            self.save()

            
    
        
    def __iter__(self):
    
        #Iterate over the items in the cart and get the products
        #from the database.

        product_ids = self.cart.keys()
        
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
            
   

 
                
            
    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    
    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
        
    

        
    
    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()
        
    
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
