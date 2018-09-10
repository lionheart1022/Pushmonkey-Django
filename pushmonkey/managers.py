from clients.managers import ClientsEmailManager
from django.conf import settings
from emails.managers import EmailManager
from models import PushPackage

MINIMUM_NUMBER_OF_PACKAGES = 15

class PushPackageManager(object):

    def get_push_package(self, profile):
        email_manager = ClientsEmailManager()
        unused_packages = PushPackage.objects.filter(used = False, website_push_id_created = True)
        if unused_packages.count():
            package = unused_packages[0]
            if unused_packages.count() < MINIMUM_NUMBER_OF_PACKAGES:
                email_manager.send_admin_almost_no_push_packages()
        else:
            package = None
            email_manager.send_admin_no_more_push_packages(profile.user.email)
        return package

class PushMonkeyEmailManager(EmailManager):

    def send_weekly_report_email(self, 
        to_email = '', 
        first_name = '', 
        subscribers = 0,
        new_subscribers = 0,
        growth = 0,
        notifications = 0
        ):
        #render email
        template_html = 'pushmonkey/email_weekly_report.html'
        subject = "%s, your weekly report is here." % first_name
        context_dict = {'first_name': first_name,
                        'total_subscribers': subscribers,
                        'new_subscribers': new_subscribers,
                        'growth': growth, 
                        'notifications_sent': notifications,
                       }
        #send email
        self.send_email(subject, template_html, context_dict, to_email)    
