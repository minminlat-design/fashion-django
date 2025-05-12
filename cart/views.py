from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        
        # Add free shippping and gift wrap to the cart login
        free_shipping = cd.get('free_shipping', False)
        gift_wrap = cd.get('gift_wrap', False)
        
        if quantity == 0:
            cart.remove(product)
        else:
            cart.add(  
                product=product,
                quantity=quantity,
                override_quantity=cd['override']
            )
            # Update cart options for free shipping and gift wrap
            # Save gift wrap option
            if cd.get('gift_wrap'):
                cart.cart['gift_wrap'] = True
            else:
                cart.cart['gift_wrap'] = False
            cart.save()
            
            cart.cart['free_shipping'] = free_shipping
            
            
        return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


@require_POST
def update_gift_wrap(request):
    cart = Cart(request)
    gift_wrap = request.POST.get('gift_wrap') == 'on'
    cart.cart['gift_wrap'] = gift_wrap
    request.session.modified = True
    return redirect('cart:cart_detail')



def cart_detail(request):
    cart = Cart(request)
    free_shipping_data = cart.get_free_shipping_progress()
    
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True}
        )
    
    context = {
        'cart': cart,
        'free_shipping_data': free_shipping_data,
    }
    
    return render(request, 'cart/cart_detail.html', context)


