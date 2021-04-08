import logging

from django.urls import reverse
from django.core.mail import send_mail
from foodgram.celery import app
from users.models import User
from foodgram import settings


@app.task
def send_verification_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        # Send verification email
        send_mail(
            subject='Регистрация на foodgram',
            message='Вы зарегестрировались на foodgram: '
                    'http://localhost:8000%s' % reverse('index_view'),
            from_email=settings.EMAIL_USE_SSL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        logging.warning(
            "Tried to send verification email to non-existing user "
            "'%s'" % user_id)
