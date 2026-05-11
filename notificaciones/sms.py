from django.conf import settings

def enviar_sms(celular, mensaje):
    """Envía SMS. Si falla, no rompe el flujo principal."""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # Colombia: asegurar formato +57
        numero = celular.strip()
        if not numero.startswith('+'):
            numero = '+57' + numero
        client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_PHONE_FROM,
            to=numero
        )
        return True
    except Exception as e:
        print(f'[SMS Error] {e}')
        return False