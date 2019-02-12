from clients.models import path_and_rename
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
import os

class WebsiteCluster(models.Model):
	creator = models.OneToOneField(User)
	created_at = models.DateTimeField(default = datetime.now)
	comment = models.CharField(max_length = 400, default = '')

	def __unicode__(self):
		return str(self.creator)

class Website(models.Model):
	account_key = models.CharField(max_length = 200, null = True, blank = True)
	cluster = models.ForeignKey(WebsiteCluster)
	comment = models.CharField(max_length = 400, default = '')
	created_at = models.DateTimeField(default = datetime.now)
	return_url = models.CharField(max_length = 400, default = '')
	website_name = models.CharField(max_length = 300, default = '')
	website_url = models.URLField()

	def __unicode__(self):
		return str(self.website_url)

	def icon(self):
		from helpers import profile_image_for_cluster
		try:
			return self.websiteicon
		except WebsiteIcon.DoesNotExist:
			profile_image = profile_image_for_cluster(self.cluster)
			return profile_image


class WebsiteIcon(models.Model):
	website = models.OneToOneField(Website)
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
		return str(self.website)

@receiver(post_delete, sender=WebsiteIcon)
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
        os.rmdir(basedir)
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)