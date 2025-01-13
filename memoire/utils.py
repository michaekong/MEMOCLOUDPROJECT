from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
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
@shared_task
def send_advanced_emails(recipient, subject, template, context):
    try:
        # Rendre le message HTML à partir du template
        html_message = render_to_string(template, context)
        
        # Créer l'objet Email
        message = EmailMultiAlternatives(subject, "", settings.EMAIL_HOST_USER, [recipient])
        message.attach_alternative(html_message, "text/html")  # Attacher le message HTML
        
        # Envoyer l'e-mail
        message.send(fail_silently=False)
    except Exception as e:
        print("Erreur lors de l'envoi de l'e-mail :", str(e))  # Pour le débogage
