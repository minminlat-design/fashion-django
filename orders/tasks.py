from celery import shared_task
from django.core.mail import send_mail
from .models import Order
from io import BytesIO
import weasyprint
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings




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
        settings.DEFAULT_FROM_EMAIL,  # Consider using settings.DEFAULT_FROM_EMAIL
        [order.email]
    )

    return f"Mail sent: {mail_sent}"






@shared_task
def payment_completed(order_id):
    try:
        order = Order.objects.get(id=order_id)

        subject = f'My Shop - Invoice no. {order.id}'
        message = 'Please, find attached the invoice for your recent purchase.'

        email = EmailMessage(
            subject, message, settings.DEFAULT_FROM_EMAIL, [order.email]
        )

        # generate PDF
        html = render_to_string('orders/order/pdf.html', {'order': order})
        out = BytesIO()
        stylesheets = [weasyprint.CSS(finders.find('css/pdf.css'))]
        weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

        # attach PDF
        email.attach(
            f'order_{order.id}.pdf', out.getvalue(), 'application/pdf'
        )

        email.send()
        return f"Invoice email sent for order {order.id}"
    
    except Order.DoesNotExist:
        return f"Order {order_id} does not exist."
    except Exception as e:
        return f"Failed to send invoice email for order {order_id}: {str(e)}"

