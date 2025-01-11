
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_advanced_email(recipient, subject, template, context):
    html_message = render_to_string(template, context)
    send_mail(
        subject,
        html_message,
        settings.EMAIL_HOST_USER,
        [recipient],
        fail_silently=False,
        html_message=html_message
    )