from django.conf import settings
from emails.managers import EmailManager

class ContactEmailManager(EmailManager):
    def send_admin_contact(self, from_email, name, message):
        template_html = 'contact_messages/email_admin_contact.html'
        subject = "New Contact message from {}".format(from_email)
        context_dict = {
            'name': name,
            'message': message
            }
        emails = [person[1] for person in settings.MANAGERS]
        self.send_email(subject, template_html, context_dict, emails)
