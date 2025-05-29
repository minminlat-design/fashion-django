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

    # --- Track all selected checkboxes
    checkbox_flags = {
        'monogram_selected': request.POST.get('jacket_monogram_selected') == 'on',
        'shirt_selected': request.POST.get('shirt_selected') == 'on',
        'vest_selected': request.POST.get('vest_selected') == 'on',
        'shirt_monogram_selected': request.POST.get('shirt_monogram_selected') == 'on',
    }
    for key, val in checkbox_flags.items():
        print(f"{key}: {val}")

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        print("Cleaned data:", cd)

        selected_options = {}

        # --- Inject base prices if checkboxes are selected
        base_price_fields = {
            'monogram': 'monogram_price',
            'shirt': 'shirt_price',
            'vest': 'vest_price',
        }

        for category, price_field in base_price_fields.items():
            if checkbox_flags.get(f'{category}_selected'):
                selected_options[category] = selected_options.get(category, {})
                selected_options[category]['price'] = {
                    'id': None,
                    'name': f"{category.title()} Base Price",
                    'price_difference': request.POST.get(price_field, '0.00')
                }

        # --- Handle shirt monogram price
        if checkbox_flags['shirt_monogram_selected']:
            selected_options['shirt'] = selected_options.get('shirt', {})
            selected_options['shirt']['monogram_price'] = {
                'id': None,
                'name': 'Shirt Monogram Price',
                'price_difference': request.POST.get('shirt_monogram_price', '0.00')
            }

        # --- Map categories to their checkbox flags for filtering
       # Categories which require explicit checkbox to be selected
        categories_with_checkboxes = {
            'monogram': 'monogram_selected',
            'shirt': 'shirt_selected',
            'vest': 'vest_selected',
            'shirt_monogram': 'shirt_monogram_selected',
        }

        # Categories always allowed, no checkbox required
        categories_always_allowed = {'jacket', 'pants', 'set'}

        # --- Parse variation dropdowns and extra price fields only if checkbox selected or category always allowed
        for key, values in request.POST.lists():
            if key in ['quantity', 'override', 'csrfmiddlewaretoken']:
                continue

            if '_' in key and not key.endswith('_price'):
                category, option_name = key.split('_', 1)

                # Allow parsing if category is in always allowed or has checkbox selected
                if category in categories_always_allowed or checkbox_flags.get(categories_with_checkboxes.get(category, ''), False):
                    selected_options.setdefault(category, {})
                    for val in values:
                        try:
                            option = VariationOption.objects.get(id=int(val))
                            selected_options[category][option_name] = {
                                'id': option.id,
                                'name': option.name,
                                'price_difference': '0.00'  # default, updated below
                            }
                        except (VariationOption.DoesNotExist, ValueError):
                            pass
                else:
                    # Not selected and not allowed category, skip
                    continue

            elif key.endswith('_price'):
                price_val = values[0] if values else '0.00'
                base_key = key[:-6]  # Strip '_price'
                category_prefix = base_key.split('_')[0]

                # Skip if category requires checkbox and it's not selected
                if category_prefix in categories_with_checkboxes:
                    checkbox_key = categories_with_checkboxes[category_prefix]
                    if not checkbox_flags.get(checkbox_key):
                        continue

                # Only proceed if category is allowed
                if category_prefix in categories_always_allowed or checkbox_flags.get(categories_with_checkboxes.get(category_prefix, ''), False):
                    for cat_opt, options in selected_options.items():
                        for opt_key, opt_data in options.items():
                            price_key_exact = f"{cat_opt}_{opt_key}_price".replace(" ", "-").lower()
                            if key.lower() == price_key_exact:
                                opt_data['price_difference'] = price_val
                                print(f"Matching price: {key} → {cat_opt}_{opt_key} → {price_val}")



        print("Final selected_options dict:", selected_options)

        # --- Customization fields (free text)
        customizations = {}
        if jacket_text := request.POST.get("jacket_monogram_text", "").strip():
            customizations["jacket_monogram_text"] = jacket_text
        if shirt_text := request.POST.get("shirt_monogram_text", "").strip():
            customizations["shirt_monogram_text"] = shirt_text

        print("Final customizations dict:", customizations)

        # --- Add to cart
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override'],
            selected_options=selected_options,
            customizations=customizations,
        )

        # --- AJAX response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            extra_price = Decimal('0.00')
            for category, options in selected_options.items():
                for option in options.values():
                    try:
                        extra_price += Decimal(option.get('price_difference', '0'))
                    except Exception:
                        pass

            unit_price = Decimal(product.discounted_price or product.price) + extra_price
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
