from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_advanced_email(recipient, subject, template_name, context):
    # Charger le template HTML
    html_message = render_to_string(template_name, context)
    
    # Créer un message texte brut
    plain_message = strip_tags(html_message)
    
    # Créer l'email
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email='memecloudenstp@gmail.com',
        to=[recipient],
        reply_to=['support@votre-domaine.com']
    )
    
    # Ajouter le contenu HTML
    email.attach_alternative(html_message, "text/html")
    
    # Envoyer l'email
    email.send()
