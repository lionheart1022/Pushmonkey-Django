from emails.managers import EmailManager
from django.conf import settings

class PlansEmailManager(EmailManager):

    def send_plan_activation(self, to_email = '', first_name = '', plan_name = ''):
        #render email
        template_html = 'plans/email_plan_activation.html'
        subject = "Let's go ahead on this new path"
        context_dict = {'first_name': first_name,
                        'plan_name': plan_name
                       }
        #send email
        self.send_email(subject, template_html, context_dict, to_email)

    def send_trial_pre_expiration(self, to_email = '', first_name = '', subscribers = 0):
        template_html = 'plans/email_trial_pre_expiration.html'
        subject = "It's almost that time"
        context_dict = {
            'first_name': first_name,
            'subscribers': subscribers,
        }
        self.send_email(subject, template_html, context_dict, to_email)

    def send_admin_new_plan(self, client_email, client_first_name, plan):
        template_html = 'plans/email_admin_new_plan.html'
        subject = client_first_name + ' selected the ' + plan.get_type_display() + ' plan'
        context_dict = {
            'client_email': client_email,
        }
        emails = [person[1] for person in settings.MANAGERS]
        for to_email in emails:
            self.send_email(subject, template_html, context_dict, to_email)
