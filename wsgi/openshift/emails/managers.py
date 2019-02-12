import os
from models import Email
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Context, loader

class EmailManager:

    def send_notif_number_exceeded(self, to_email, first_name, remaining_days, subscribers, next_plan_name):
        #render email
        template_html = 'emails/notif_number_exceeded.html'
        subject = "Number of notifications exceeded - Push Monkey"
        context_dict = {'first_name': first_name,
                        'remaining_days': remaining_days,
                        'subscribers': subscribers,
                        'next_plan_name': next_plan_name,
                       }
        #send email
        self.send_email(subject, template_html, context_dict, to_email)

    def render_content(self, template_html, context_dictionary):
        (root, ext) = os.path.splitext(template_html)
        template_text = root + '.txt'
        text = loader.get_template(template_text)
        html = loader.get_template(template_html)
        context = Context(context_dictionary)
        text_content = text.render(context)
        html_content = html.render(context)
        return text_content, html_content 

    def mark_in_database(self, subject = '', to_email = ''):
        email = Email(subject = subject, to_email = to_email)
        email.save()

    def send_email(self, subject, template_html, context_dict, to_email):
        """
        Actually sends an email and marks this in the database

        subject - email subject
        template_html - path of the html_template used
        context_dict - the context required by the template
        to_email - the receiver of this email. Can be a string or a list of strings.
        """
        text_content, html_content = self.render_content(template_html, context_dict)
        from_email = settings.DEFAULT_FROM_EMAIL
        if not isinstance(to_email, list):
            to_email = [to_email]
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        #mark in the database
        self.mark_in_database(subject = subject, to_email = to_email)
