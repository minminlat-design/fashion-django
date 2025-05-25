from decimal import Decimal
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string



# Classic and Ajax updating code for quantites
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            unit_price = Decimal(product.discounted_price or product.price)
            item_total = unit_price * cd['quantity']
            return JsonResponse({
                'success': True,
                'quantity': cd['quantity'],
                'total_price': f"{cart.get_total_price():.2f}",
                'item_total': f"{item_total:.2f}"
            })
    return redirect('cart:cart_detail')





@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    cart.save()

    return JsonResponse({
        'success': True,
        'total_price': f"{cart.get_total_price():.2f}",
        'item_count': len(cart),
    })


    

def cart_detail(request):
    cart = Cart(request)
    free_shipping_data = cart.get_free_shipping_data()
    
    # Updating the quantities
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
        initial={'quantity': item['quantity'], 'override': True}
        )
    return render(request, 'cart/detail.html', {
        'cart': cart,
        'free_shipping_data': free_shipping_data,
    })


@require_GET
def cart_shipping_info(request):
    cart = Cart(request)
    free_shipping_data = cart.get_free_shipping_data()

    return JsonResponse({
        'progress': free_shipping_data['progress'],
        'remaining': str(free_shipping_data['remaining']),
        'qualified': free_shipping_data['qualified'],
    })
   
   
@require_POST
def cart_update_quantity(request):
    cart = Cart(request)
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)

        if quantity < 1:
            quantity = 1

        cart.update(product, quantity)
        cart.save()

        item_total = cart.get_item_total(product)
        total_price = cart.get_total_price()

        return JsonResponse({
            "success": True,
            "item_total": f"{item_total:.2f}",
            "total_price": f"{total_price:.2f}",
            "quantity": quantity,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


