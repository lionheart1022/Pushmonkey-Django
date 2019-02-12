from emails.managers import EmailManager
from django.core.urlresolvers import reverse

class AffiliateEmailManager(EmailManager):

    def send_welcome_email(self, to_email, first_name, token):
        #render email
        template_html = 'affiliates/email_welcome.html'
        subject = "Welcome to Push Monkey Affiliate Program. You rock!"
        subject = first_name + ", welcome to the Push Monkey Affiliate Program"
        affiliate_url = 'http://www.getpushmonkey.com/af/' + token
        affiliate_center_url = 'http://www.getpushmonkey.com' + reverse('affiliates_center')
        context_dict = {'first_name': first_name,
                        'affiliate_url': affiliate_url,
                        'affiliate_center_url': affiliate_center_url
                       }
        #send email
        self.send_email(subject, template_html, context_dict, to_email)

    def send_payout_request_email(self, affiliate_email):
        emails = [person[1] for person in settings.MANAGERS]
        subject = affiliate_email + ' requested a payout of his affiliate commissions'
        message = 'Go to getpushmonkey.com/admin/affiliates/, to check out the current status.'
        from_email = settings.DEFAULT_FROM_EMAIL           
        msg = EmailMultiAlternatives(subject, message, from_email, emails)
        msg.send()
