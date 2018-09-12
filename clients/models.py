from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from uuid import uuid4
from django.utils.text import Truncator
import hashlib
import os
import pushmonkey 
import string, random
from django.utils.text import slugify

REGISRATION_STEP = (
    (1, 'Registration'),
    (2, 'Customise'),
    (3, 'Overview'),
    (4, 'Finished')
)

STATUS_CHOICES = (
    ('pending', 'Pending Account Key'),
    ('active', 'Active'),
)

class ClientProfile(models.Model):
    user = models.OneToOneField(User)
    account_key = models.CharField(max_length=200, null=True, blank = True)
    website_push_id = models.CharField(max_length=200, null=True, blank = True)
    url_format_string = models.CharField(max_length=200, default='', blank = True)
    confirmed = models.BooleanField(default=False)
    preselected_plan = models.CharField(null = True, blank = True, default='', max_length = '5',
                                        help_text = "Pre-selected pricing plan. Valus can be in the format &lt;plan-index&gt;-&lt;plan-length&gt; e.g. 1-M, 2-Y")
    status = models.CharField(max_length = 30, default = STATUS_CHOICES[0][0], choices = STATUS_CHOICES)
    registration_step = models.IntegerField(default = REGISRATION_STEP[0][0], choices = REGISRATION_STEP)
    created_at = models.DateTimeField(default=datetime.now)
    website = models.URLField()
    website_name = models.CharField(max_length = 300, default = '')
    return_url = models.CharField(max_length = 400, default = '', blank = True)
    from_envato = models.BooleanField(default = False)
    subdomain = models.CharField(max_length = 60, null=True, blank = True)

    def __unicode__(self):
        return self.user.username

    def is_pending(self):
        return self.status == 'pending'

    def save(self, *args, **kwargs):
        if not self.subdomain and self.website_name:
            slug = slugify(self.website_name)
            slug = Truncator(slug).chars(30, truncate="")
            count = ClientProfile.objects.filter(subdomain = slug).count()
            if count == 0:
                self.subdomain = slug
            else:
                self.subdomain = "%s-%s" % (slug, count+1)
        super(ClientProfile, self).save(*args, **kwargs)

    def has_push_package(self):
        try:
            package = pushmonkey.models.PushPackage.objects.get(identifier = self.account_key)
        except:
            package = None
        if package:
            if os.path.exists(package.path()):
                return True
        return False
    has_push_package.short_description = "Has Push Package"
    has_push_package.boolean = True


class ProfileConfirmation(models.Model):
    profile = models.OneToOneField(ClientProfile)
    confirmation_key = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)
    confirmed_at = models.DateTimeField(null=True)
    number_of_resends = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.profile)

def path_and_rename(path):
    def wrapper(instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = '{}.{}'.format(instance.pk, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(path, filename)
    return wrapper

class ProfileImage(models.Model):
    profile = models.OneToOneField(ClientProfile)
    image = models.ImageField(upload_to = path_and_rename('profile_images'), max_length=400, default='')
    image128_2x = ImageSpecField(source='image',
                                 processors=[ResizeToFill(256, 256)],
                                 format='PNG')
    image128 = ImageSpecField(source='image',
                              processors=[ResizeToFill(128, 128)],
                              format='PNG')
    image32_2x = ImageSpecField(source='image',
                                processors=[ResizeToFill(64, 64)],
                                format='PNG')
    image32 = ImageSpecField(source='image',
                             processors=[ResizeToFill(32, 32)],
                             format='PNG')
    image16_2x = ImageSpecField(source='image',
                                processors=[ResizeToFill(32, 32)],
                                format='PNG')
    image16 = ImageSpecField(source='image',
                             processors=[ResizeToFill(16, 16)],
                             format='PNG')
    def __unicode__(self):
        return str(self.profile)

@receiver(post_delete, sender=ProfileImage)
def profile_image_delete(sender, instance, **kwargs):
    # Remove ImageKit versions
    basedir = os.path.dirname(instance.image128.path)
    paths = [instance.image128_2x.path, 
             instance.image128.path,
             instance.image32_2x.path,
             instance.image32.path,
             instance.image16_2x.path,
             instance.image16.path,
            ]
    for img_path in paths:
        if os.path.exists(img_path):
            os.remove(img_path)
    normalised_media_root = os.path.normpath(settings.MEDIA_ROOT)
    if not basedir == normalised_media_root:
        try:
            os.rmdir(basedir)
        except Exception, e:
            print e
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)
