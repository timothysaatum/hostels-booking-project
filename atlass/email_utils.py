from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
import smtplib

@transaction.atomic
def send_email_with_transaction(subject, message, from_email, recipient_list):

	with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()

		smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
		msg = f'Subject: {subject}\n\n{message}'
		
		smtp.sendmail(settings.EMAIL_HOST_USER, 'saatumtimothy@gmail.com', msg)