from clients.models import ClientProfile, ProfileImage
from datetime import datetime, timedelta
from djacobs_apns.apns import APNs, Payload
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django_push_package.push_package import PushPackage as PushPackageMaker
import string, random, os, json, shutil, urlparse


class Device(models.Model):
    token = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True, default=datetime.now)
    account_key = models.CharField(max_length=200, null=True)
    ported = models.BooleanField(help_text = "Indicates a device ported from a previous version, that used a direct urlFormatString in website.json", default = False)
    comment = models.CharField(max_length = 200, default = '')

    def __unicode__(self):
        return self.token

class WebServiceDevice(models.Model):

    subscription_id = models.CharField(max_length=200)
    endpoint = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True, default=datetime.now)
    account_key = models.CharField(max_length=200, null=True)
    comment = models.CharField(max_length = 200, default = '', blank = True)
    mozilla = models.BooleanField(help_text = 'Indicates whether this is a Firefox device.', default = False)
    chrome = models.BooleanField(help_text = 'Indicates whether this is a Chrome device.', default = False)

    def __unicode__(self):
        return self.subscription_id


class StatisticsManager(models.Manager):
    """
    NOTE: these methods apply only on the manager, not on the QuerySets
    """
    def sent_notifications_count(self, account_key = None):
        """
        Return an integer representing the total number
        of notifications sent by an account_key. 
        """
        sent_notifications = 0
        today = datetime.now()
        for notif in self.filter(account_key = account_key, created_at__year = today.year, created_at__month = today.month):
            sent_notifications += int(notif.device_num)
        return sent_notifications

    def sent_and_opened_datasets(self, number_of_days = 7, account_key = None):
        """
        Return the dataset of sent notifications and opened notifications
        for an account_key and a number_of_days, representing the number of historical days
        """
        sent_notifications_dataset = []
        opened_notifications_dataset = []
        for i in range(0, number_of_days):
            prev_date = datetime.today()-timedelta(days=i)
            day = prev_date.day
            month = prev_date.month
            messages = self.filter(account_key = account_key, created_at__day = day, created_at__month = month)
            sent_total = 0
            opened_total = 0
            for message in messages:
                sent_total = sent_total + int(message.device_num)
                opened_total = opened_total + message.opened_num
            sent_notifications_dataset.append(sent_total) 
            opened_notifications_dataset.append(opened_total)

        sent_notifications_dataset.reverse()
        opened_notifications_dataset.reverse()

        return sent_notifications_dataset, opened_notifications_dataset

    def labels_dataset(self, number_of_days = 7):
        labels_dataset = []
        for i in range(0, number_of_days):
            day = datetime.today()-timedelta(days=i)
            formated_day = day.strftime('%b %d')
            labels_dataset.append(formated_day)
        labels_dataset.reverse()
        return labels_dataset

class PushMessage(models.Model):
    title = models.CharField(max_length=200)
    body = models.CharField(max_length=200)
    url_args = models.CharField(max_length=200, default="")
    device_num = models.CharField(max_length=10, default="0")
    opened_num = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now, editable=True)
    account_key = models.CharField(max_length=200, null=True)
    comment = models.CharField(max_length = 300, default="")
    custom = models.BooleanField(default = False)

    objects = StatisticsManager()

    def __unicode__(self):
        return self.title

class PayloadSafari(Payload):

    def __init__(self, alert=None, url_args=[]):
        super(Payload, self).__init__()
        self.alert = alert
        self.url_args = url_args
        self._check_size()

    def dict(self):
        d = {"alert": self.alert, "url-args": self.url_args}
        d = {'aps': d}
        #print d
        return d

def path_with_identifier(path, target_filename):
    def wrapper(instance, filename):
        return os.path.join(path, instance.identifier, target_filename)
    return wrapper

class PushPackage(models.Model):
    key_pem = models.FileField(upload_to = path_with_identifier('push_packages', 'key.pem'), null = True, blank = True) 
    cert_pem = models.FileField(upload_to = path_with_identifier('push_packages', 'cert.pem'), null = True, blank = True) 
    cert_p12 = models.FileField(upload_to = path_with_identifier('push_packages', 'cert.p12'), null = True, blank = True)
    used = models.BooleanField(default = False)
    website_push_id_created = models.BooleanField(help_text = "If checked, it means that a Website Push ID and certificates were created on Apple's Dev Center", default = False)
    identifier = models.CharField(max_length = 50, default = "", blank = True)
    website_push_id = models.CharField(max_length = 100, default = "", null = True, blank = True)
    created_at = models.DateTimeField(default = datetime.now)
    updated_at = models.DateTimeField(auto_now = True, default = datetime.now)

    def __unicode__(self):
        return self.identifier

    def save(self, *args, **kwargs):
        if not self.pk:
            self.identifier = ''.join(random.sample(string.uppercase + '1234567890', 17)) 
            self.website_push_id = 'web.com.pushmonkey.' + self.identifier
        super(PushPackage, self).save(*args, **kwargs)

    def path(self):
        dirname = os.path.dirname(self.key_pem.path)
        return os.path.join(dirname, 'pushPackage.zip')

    def websites_from_website(self, website):
        r = urlparse.urlparse(website)
        has_www = r.hostname.startswith('www')
        domain = r.hostname
        if has_www:
            domain = '.'.join(r.hostname.split('.')[1:])
        return [
            urlparse.urlunsplit(['http', domain, '', '', '']),
            urlparse.urlunsplit(['https', domain, '', '', '']),
            urlparse.urlunsplit(['http', 'www.' + domain, '', '', '']),
            urlparse.urlunsplit(['https', 'www.' + domain, '', '', '']),
        ]

    def prepare_for_reuse(self):
        try:
            dirname = os.path.dirname(self.key_pem.path)
            website_json_path = os.path.join(dirname, 'website.json')
            if os.path.exists(website_json_path):
                os.remove(website_json_path)
            push_package_path = os.path.join(dirname, 'pushPackage.zip')
            if os.path.exists(push_package_path):
                os.remove(push_package_path)
            iconset_path = os.path.join(dirname, 'iconset')
            if os.path.exists(iconset_path) and os.path.isdir(iconset_path):
                shutil.rmtree(iconset_path)
            self.used = False
            self.save()
            return True
        except Exception, e:
            return False

    #TODO: move this to a manager
    def generate_zip(self, 
                     website_name, 
                     website,
                     icon128_2x_path,
                     icon128_path,
                     icon32_2x_path,
                     icon32_path,
                     icon16_2x_path,
                     icon16_path 
                    ):
        # check certificates
        if not self.key_pem or not self.cert_pem or not self.cert_p12:
            raise Exception('Certificate files are missing for PushPackage with identifier: ' + self.identifier)
        # create website.json
        site = Site.objects.get_current()
        website_variants = self.websites_from_website(website)
        website_json = {
            "websiteName": website_name,
            "websitePushID": self.website_push_id,
            "allowedDomains": website_variants,
            "urlFormatString": "https://" + site.domain + "/stats/track_open/%@",
            "authenticationToken": self.identifier,
            "webServiceURL": "https://" + site.domain + "/push"
        }
        dirname = os.path.dirname(self.key_pem.path)
        website_json_path = os.path.join(dirname, 'website.json')
        with open(website_json_path, 'w') as outfile:
            json.dump(website_json, outfile)
        # create icons
        iconset_path = os.path.join(dirname, 'iconset')
        os.makedirs(iconset_path)
        shutil.copyfile(icon128_2x_path, os.path.join(iconset_path, 'icon_128x128@2x.png'))
        shutil.copyfile(icon128_path, os.path.join(iconset_path, 'icon_128x128.png'))
        shutil.copyfile(icon32_2x_path, os.path.join(iconset_path, 'icon_32x32@2x.png'))
        shutil.copyfile(icon32_path, os.path.join(iconset_path, 'icon_32x32.png'))
        shutil.copyfile(icon16_2x_path, os.path.join(iconset_path, 'icon_16x16@2x.png'))
        shutil.copyfile(icon16_path, os.path.join(iconset_path, 'icon_16x16.png'))
        # generate the .zip
        p = PushPackageMaker()
        p.create(workdir = dirname)

class Batch(models.Model):
    resp = models.TextField()
    push_message = models.ForeignKey(PushMessage)
    updated_at = models.DateTimeField(auto_now = True, default = datetime.now)
    created_at = models.DateTimeField(auto_now_add = True, default = datetime.now)

    def __unicode__(self):
        return self.push_message.title

    class Meta:
        verbose_name_plural = "batches"

