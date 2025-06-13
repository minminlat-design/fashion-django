from django.db import transaction
from decimal import Decimal
from cart.cart import Cart 
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from cart.models import CartItem
from fashion_01 import settings
from orders.models import Order, OrderItem
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ShippingForm
from django.shortcuts import render, redirect
import stripe
from orders.tasks import order_created






def create_order_from_cart(user, shipping_data):
    """
    shipping_data is a dict with keys like first_name, last_name, email, address, postal_code, city
    """
    cart_items = CartItem.objects.filter(user=user, is_active=True)
    if not cart_items.exists():
        raise ValueError("Cart is empty")

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            first_name=shipping_data['first_name'],
            last_name=shipping_data['last_name'],
            email=shipping_data['email'],
            address=shipping_data['address'],
            postal_code=shipping_data['postal_code'],
            city=shipping_data['city'],
            phone=shipping_data['phone'],        # ✅ Add this
            country=shipping_data['country'],    # ✅ Add this
            paid=False,
            status='pending',
            total_price=Decimal('0')
        )

        total_price = Decimal('0')
        for ci in cart_items:
            
            print(f"[DEBUG] frozen_measurement_data for {ci.product.name}: {ci.frozen_measurement_data} ({type(ci.frozen_measurement_data)})")
            frozen_data = ci.frozen_measurement_data or {}


            oi = OrderItem.objects.create(
                order=order,
                product=ci.product,
                product_name=ci.product.name,
                quantity=ci.quantity,
                base_price=ci.base_price,
                total_price=ci.total_price,
                gift_wrap=ci.gift_wrap,
                #frozen_measurement_data=ci.frozen_measurement_data,
                frozen_measurement_data=frozen_data,
                selected_options=ci.selected_options,
                customizations=ci.customizations,
                user_measurement=ci.user_measurement,

            )
            print(f"[DEBUG] Saved OrderItem frozen data: {oi.frozen_measurement_data}")

            total_price += oi.total_price

            ci.is_active = False
            ci.save()
            
        print(f"[DEBUG] Copying frozen data to OrderItem: {ci.frozen_measurement_data}")


        order.total_price = total_price
        order.save()

    return order




@login_required
def shipping_info_view(request):
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            request.session['shipping_info'] = {
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'address': data['address'],
                'postal_code': data['postal_code'],
                'city': data['city'],
                'phone': data['phone'],        # ✅ Add this
                'country': data['country'],    # ✅ Add this
            }
            print("[DEBUG] Shipping info saved:", request.session['shipping_info'])
            return redirect('orders:review_order')  # Next step
    else:
        # Use session data to pre-fill the form if available
        initial_data = request.session.get('shipping_info')
        form = ShippingForm(initial=initial_data)

    subtotal = sum(item.total_price for item in cart_items)

    return render(request, 'orders/shipping_info.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
    })



stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def review_order_view(request):
    shipping_info = request.session.get('shipping_info')
    if not shipping_info:
        messages.error(request, "Shipping information is missing.")
        return redirect('orders:shipping_info')

    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    subtotal = sum(item.total_price for item in cart_items)

    if request.method == 'POST':
        # Create Order
        order = create_order_from_cart(request.user, shipping_info)
        
        # Trigger async email
        order_created.delay(order.id)

        # Create Stripe Checkout Session
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(item.total_price * 100),  # in cents
                    'product_data': {
                        'name': item.product_name,
                    },
                },
                'quantity': item.quantity,
            } for item in order.items.all()
        ]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('orders:payment_success')),
            cancel_url=request.build_absolute_uri(reverse('orders:payment_cancel')),
            metadata={'order_id': order.id},
            client_reference_id=order.id 
        )

        return redirect(checkout_session.url, code=303)

    return render(request, 'orders/review_order.html', {
        'shipping_info': shipping_info,
        'cart_items': cart_items,
        'subtotal': subtotal,
    })







 
@login_required
def payment_success_view(request):
    # Clear session-based cart
    cart = Cart(request)
    cart.clear()

    # Clear DB-based cart items
    CartItem.objects.filter(user=request.user, is_active=True).delete()

    # Clear session shipping info if present
    request.session.pop('shipping_info', None)

    messages.success(request, "Payment successful! Thank you for your order.")
    return render(request, 'orders/payment_success.html')




@login_required
def payment_cancel_view(request):
    messages.warning(request, "Payment was canceled.")
    return render(request, 'orders/payment_cancel.html')
