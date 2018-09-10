from django.db import models
from clients.models import ClientProfile
from pushmonkey.models import Device, WebServiceDevice
from datetime import datetime

class Segment(models.Model):
  name = models.CharField(max_length = 100)
  account_key = models.CharField(max_length = 200)
  client = models.ForeignKey(ClientProfile, null = True, blank = True)
  device = models.ManyToManyField(Device, null = True, blank = True)
  web_service_device = models.ManyToManyField(WebServiceDevice, null = True, blank = True)
  updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
  created_at = models.DateTimeField(auto_now_add=True, default=datetime.now)

  def __unicode__(self):
    return "%s - %s" % (self.name, self.account_key)

  def subscriber_count(self):
    return self.device.count() + self.web_service_device.count()
