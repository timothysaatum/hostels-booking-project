#from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from textwrap import dedent


def send_email_with_transaction(subject, body, recipient_list):
	email_from = settings.EMAIL_HOST_USER
	body = dedent(body)
	send_mail(subject, body, email_from, recipient_list)



def create_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html = template.render(context_dict)
	result = BytesIO()

	receipt = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

	if not receipt.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None