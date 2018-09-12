from django.conf import settings
from emails.managers import EmailManager

class ClientsEmailManager(EmailManager):
    def send_confirmation_link_email(self, to_email = '', first_name = '', confirmation_key = ''):
        #render email
        template_html = 'clients/email_confirmation_link.html'
        subject = first_name + ", let's start. Your readers are waiting!"
        confirmation_link = 'https://www.getpushmonkey.com/confirm/' + confirmation_key
        context_dict = {'first_name': first_name,
                        'confirmation_link': confirmation_link,
                       }
        #send email
        self.send_email(subject, template_html, context_dict, to_email)

    def send_welcome_email(self, to_email = '', first_name = ''):
        template_html = 'clients/email_welcome.html'
        subject = "You're in! Push Monkey is NOT for everyone"
        context_dict = {'first_name': first_name,
            }
        self.send_email(subject, template_html, context_dict, to_email)

    def send_account_key_email(self, to_email = '', first_name = '', account_key = ''):
        template_html = 'clients/email_account_key.html'
        subject = "Good news, everybody! Your Account Key is here - Push Monkey"
        context_dict = {
            'first_name': first_name,
            'account_key': account_key,
        }
        self.send_email(subject, template_html, context_dict, to_email)

    def send_website_invitation(self, email, website_name, id):
        template_html = 'clients/email_website_invitation.html'
        subject = "Invitation to manage push notification for %s" % website_name
        context = {
            "link": "https://www.getpushmonkey.com/accept/%s" % id,
            "website_name": website_name
        }
        self.send_email(subject, template_html, context, email)

    def send_admin_new_client(self, client_email):
        template_html = 'clients/email_admin_new_client.html'
        subject = "Capt'n, " + client_email + " signed up."
        emails = [person[1] for person in settings.MANAGERS]
        self.send_email(subject, template_html, {}, emails)
    
    def send_admin_no_more_push_packages(self, client_email):
        template_html = 'clients/email_admin_no_more_push_packages.html'
        subject = "Capt'n, " + client_email + " signed up and there are no more push packages"
        context_dict = {}
        emails = [person[1] for person in settings.MANAGERS]
        self.send_email(subject, template_html, context_dict, emails)

    def send_admin_almost_no_push_packages(self):
        template_html = 'clients/email_admin_almost_no_push_packages.html'
        subject = "Capt'n, there are only a few unused push packages left"
        context_dict = {}
        emails = [person[1] for person in settings.MANAGERS]
        self.send_email(subject, template_html, context_dict, emails)