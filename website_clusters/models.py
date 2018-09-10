from clients.models import path_and_rename
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.utils.text import Truncator
import os
from django.utils.text import slugify

class WebsiteCluster(models.Model):
  creator = models.OneToOneField(User)
  created_at = models.DateTimeField(default = datetime.now)
  comment = models.CharField(max_length = 400, default = '')
  max_number_of_websites = models.IntegerField(default = 5)

  def __unicode__(self):
    return str(self.creator)

class Website(models.Model):
  account_key = models.CharField(max_length = 200, null = True, blank = True)
  agent = models.ForeignKey(User, null = True, blank = True)
  cluster = models.ForeignKey(WebsiteCluster)
  comment = models.CharField(max_length = 400, default = '', blank = True)
  created_at = models.DateTimeField(default = datetime.now)
  return_url = models.CharField(max_length = 400, default = '', blank = True)
  subdomain = models.CharField(max_length = 60, null=True, blank = True)
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

  def save(self, *args, **kwargs):
      if not self.subdomain and self.website_name:
          slug = slugify(self.website_name)
          slug = Truncator(slug).chars(30, truncate="")
          count = Website.objects.filter(subdomain = slug).count()
          if count == 0:
              self.subdomain = slug
          else:
              self.subdomain = "%s-%s" % (slug, count+1)
      super(Website, self).save(*args, **kwargs)      


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

class WebsiteInvitation(models.Model):
  accepted = models.BooleanField(default = False)
  created_at = models.DateTimeField(default = datetime.now)
  email = models.EmailField()
  resent = models.IntegerField(default = 0)
  updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
  website = models.ForeignKey(Website)

  def __unicode__(self):
    return "%s - %s" % (self.website, self.email)

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