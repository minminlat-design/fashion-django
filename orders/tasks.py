from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f"Order {order_id} does not exist."

    subject = f'Order #{order.id} Confirmation'
    message = (
        f'Dear {order.first_name},\n\n'
        f'Thank you for your purchase!\n'
        f'Your order (ID: {order.id}) has been received and is now being processed.\n\n'
        f'We will notify you once it ships.\n\n'
        f'Best regards,\nThe MyShop Team'
    )

    mail_sent = send_mail(
        subject,
        message,
        'admin@myshop.com',  # Consider using settings.DEFAULT_FROM_EMAIL
        [order.email]
    )

    return f"Mail sent: {mail_sent}"
