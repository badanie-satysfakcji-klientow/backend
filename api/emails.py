from django.core.mail import send_mass_mail
from django.core.mail import get_connection, EmailMultiAlternatives
from threading import Thread
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
# from django.urls import reverse


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)


def send_my_mass_mail(survey_id, survey_title, email_list, html=True) -> None:
    """
    starts new thread sending mass email (to prevent API freeze) - significantly speeds up the request
    current link to survey: DOMAIN_NAME/survey/<survey_id>
    """
    # partial_link = reverse('surveys-uuid', args=[survey_id])
    # partial_link = partial_link.replace('surveys', 'survey')
    # ^ pointless

    partial_link = f'/survey/{survey_id}'
    survey_link = settings.DOMAIN_NAME + partial_link

    context = {'link': survey_link}
    html_message = render_to_string('email_template.html', context=context)
    txt_message = strip_tags(html_message)

    if html:
        data_tuple_html = ((survey_title, txt_message, html_message, None, email_list),)
        t = Thread(target=send_mass_html_mail, args=(data_tuple_html,))
        t.start()
    else:
        data_tuple_txt = ((survey_title, txt_message, None, email_list),)
        t = Thread(target=send_mass_mail, args=(data_tuple_txt,))
        t.start()
