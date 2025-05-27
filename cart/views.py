from decimal import Decimal
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from store.models import Product, ProductVariation
from variation.models import VariationOption
from .cart import Cart, CartSettings
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    print("Request POST data:", request.POST)
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        print("Cleaned data:", cd)

        # === Improved selected_options logic ===
        selected_options = {}

        for key, values in request.POST.lists():
            if '_' in key:
                category, option_name = key.split('_', 1)
                if category not in selected_options:
                    selected_options[category] = {}
                for val in values:
                    try:
                        option = VariationOption.objects.get(id=int(val))
                        selected_options[category][option_name] = {
                            'id': option.id,
                            'name': option.name,
                            'price_difference': str(option.price_difference)
                        }
                    except (VariationOption.DoesNotExist, ValueError):
                        continue


        print("Final selected_options dict:", selected_options)

        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override'],
            selected_options=selected_options,
            customizations={},  # Add monogram text etc. if needed
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
    gift_wrap_status = cart.gift_wrap

    try:
        settings_obj = CartSettings.objects.latest('id')
    except CartSettings.DoesNotExist:
        settings_obj = CartSettings(
            free_shipping_threshold=Decimal('300.00'),
            gift_wrap_price=Decimal('5.00')
        )

    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True}
        )

    return render(request, 'cart/detail.html', {
        'cart': cart,
        'free_shipping_data': free_shipping_data,
        'gift_wrap': gift_wrap_status,
        'gift_wrap_price': settings_obj.gift_wrap_price,
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
        cart_key = data.get('cart_key')
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            quantity = 1

        # ✅ Extract selected_options and customizations from session cart
        cart_item = cart.cart.get(cart_key)
        if not cart_item:
            return JsonResponse({"success": False, "error": "Item not found in cart"})

        selected_options = cart_item.get('selected_options', {})
        customizations = cart_item.get('customizations', {})

        # ✅ Get product by cart_key
        product = cart.get_product_by_key(cart_key)
        if not product:
            return JsonResponse({"success": False, "error": "Invalid product"})

        # ✅ Update cart
        cart.update(product, quantity, selected_options, customizations)
        cart.save()

        item_total = cart.get_item_total(product, selected_options, customizations)
        total_price = cart.get_total_price()

        return JsonResponse({
            "success": True,
            "item_total": f"{item_total:.2f}",
            "total_price": f"{total_price:.2f}",
            "quantity": quantity,
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@require_POST
def toggle_gift_wrap(request):
    data = json.loads(request.body)
    enable = data.get('enable', False)

    cart = Cart(request)
    cart.toggle_gift_wrap(enable)

    return JsonResponse({
        'success': True,
        'gift_wrap': cart.gift_wrap,
        'total_price': str(cart.get_total_price()),
    })
