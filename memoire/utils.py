
from django.template.loader import render_to_string

import logging
from django.conf import settings
from  django.core.mail  import send_mail
logger=logging.getLogger(__name__)

def send_advanced_email(recipient :list, subject:str, template :str, context:dict):
    # Charger le template HTML
    try:
        html_message = render_to_string(template, context)
        

        send_mail(
            subject,
            html_message,
            settings.EMAIL_HOST_USER,
            recipient,
            fail_silently=False,
            html_message=html_message  
            )
        return True

       
    except Exception as e :
        logger.error(e)    
    return False    
