from clients.managers import ClientsEmailManager
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
