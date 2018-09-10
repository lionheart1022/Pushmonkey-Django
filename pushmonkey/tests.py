from clients.models import ClientProfile, ProfileImage
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from management.commands.send_push import Command as SendPushCommand
from management.commands.weekly_report import Command as WeeklyReportCommand
from managers import PushPackageManager
from models import PushPackage, Device, WebServiceDevice, PushMessage
from segments.models import Segment
import os

c = Client()

class PushMonkeyTests(TestCase):

  def test_website_generation(self):
    p = PushPackage()
    website = 'https://wptest-pushmonkey.rhcloud.com/'
    websites = p.websites_from_website(website)
    expected = ['http://wptest-pushmonkey.rhcloud.com', 
    'https://wptest-pushmonkey.rhcloud.com', 
    'http://www.wptest-pushmonkey.rhcloud.com', 
    'https://www.wptest-pushmonkey.rhcloud.com']
    self.assertEqual(len(websites), 4)
    self.assertEqual(websites, expected)

  def test_website_generation_with_www(self):
    p = PushPackage()
    website = 'http://www.orthospinedistributors.com/'
    websites = p.websites_from_website(website)
    expected = ['http://orthospinedistributors.com', 
    'https://orthospinedistributors.com', 
    'http://www.orthospinedistributors.com', 
    'https://www.orthospinedistributors.com']
    self.assertEqual(len(websites), 4)
    self.assertEqual(websites, expected)

  def test_website_generation_with_https(self):
    p = PushPackage()
    website = 'https://www.orthospinedistributors.com/'
    websites = p.websites_from_website(website)
    expected = ['http://orthospinedistributors.com', 
    'https://orthospinedistributors.com', 
    'http://www.orthospinedistributors.com', 
    'https://www.orthospinedistributors.com']
    self.assertEqual(len(websites), 4)
    self.assertEqual(websites, expected)

  def test_device_registration_no_push_package(self):
    push_package = PushPackage(website_push_id = 'web.com.pushmonkey.1', 
      used = True, identifier = "B1")
    push_package.save()
    user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    profile = ClientProfile(website_push_id = 'web.com.pushmonkey.1', user = user)
    profile.save()
    response = c.post(reverse('apn_device_register', 
      args = ["ABC", push_package.website_push_id]))
    added_devices_count = Device.objects.all().count()
    resp = c.delete(reverse('apn_device_register', 
      args = ["ABC", push_package.website_push_id]))
    deleted_devices_count = Device.objects.all().count()

    self.assertTrue(profile.id > 0)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(added_devices_count, 1)
    self.assertEqual(deleted_devices_count, 0)

  def test_device_registration(self):
    user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    profile = ClientProfile(website_push_id = 'web.com.pushmonkey.1', user = user)
    profile.save()
    push_package = PushPackage(website_push_id = 'web.com.pushmonkey.1', used = True, identifier = "B1")
    push_package.save()
    response = c.post(reverse('apn_device_register', 
      args = ["ABC", push_package.website_push_id]))
    added_devices_count = Device.objects.all().count()
    resp = c.delete(reverse('apn_device_register', 
      args = ["ABC", push_package.website_push_id]))
    deleted_devices_count = Device.objects.all().count()

    self.assertTrue(profile.id > 0)
    self.assertTrue(push_package.id > 0)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(added_devices_count, 1)
    self.assertEqual(deleted_devices_count, 0)

  def test_get_push_package(self):

    user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    profile = ClientProfile(website_push_id = 'web.com.pushmonkey.1', user = user)
    profile.save()
    manager = PushPackageManager()
    p1 = manager.get_push_package(profile)
    outbox_count1 = len(mail.outbox)
    for n in range(0, 5):
      p = PushPackage()
      p.website_push_id_created = True
      p.save()
    ps = PushPackage.objects.all()
    p2 = manager.get_push_package(profile)
    outbox_count2 = len(mail.outbox)

    self.assertEqual(ps.count(), 5)
    self.assertTrue(p1 == None)
    self.assertTrue(p2 != None)
    self.assertEqual(outbox_count1, 1)
    self.assertEqual(outbox_count2, 2)

  def test_weekly_report(self):
    user = User.objects.create_user('john', 'tudorizer@gmail.com', 'johnpassword')
    user.first_name = "Tudor"
    user.save()
    message = PushMessage.objects.create(title = "yo", 
      body = "body", 
      account_key = "123")
    profile = ClientProfile(account_key = "123", 
      confirmed = True,
      status = "active", 
      registration_step = 4,            
      website_push_id = 'web.com.pushmonkey.1', 
      user = user)
    profile.save()
    d1 = Device.objects.create(account_key = "123", token = "abc")
    d2 = Device.objects.create(account_key = "123", token = "abcd")
    d3 = Device.objects.create(account_key = "123", token = "abcdx")        
    d3.created_at = datetime.now() - timedelta(days = 8)
    d3.save()

    command = WeeklyReportCommand()
    command.handle()
    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(len(mail.outbox[0].alternatives), 1)
    html = mail.outbox[0].alternatives[0]
    self.assertIn("Total Subscribers  \n\n3", mail.outbox[0].body)
    self.assertIn("New Subscribers\n\n2\n\n%2 growth", mail.outbox[0].body)

class SendPushTests(TestCase):

  def test_devices(self):
    d1 = Device.objects.create(account_key = "123", token = "abc")
    d2 = Device.objects.create(account_key = "123", token = "xyz")
    d3 = Device.objects.create(account_key = "123", token = "ijk")        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg1.device.add(d1)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    seg2.device.add(d3)
    seg2.save()
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    message.segments.add(seg1, seg2)
    message.save()
    command = SendPushCommand()
    devices = command.get_devices(message)

    # include devices that have not subcribed to any segment
    self.assertEqual(len(devices), 3)

  def test_devices_single_segment(self):
    d1 = Device.objects.create(account_key = "123", token = "abc")
    d2 = Device.objects.create(account_key = "123", token = "xyz")
    d3 = Device.objects.create(account_key = "123", token = "ijk")        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg1.device.add(d1)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    message.segments.add(seg1, seg2)
    message.save()
    command = SendPushCommand()
    devices = command.get_devices(message)

    # include devices that have not subcribed to any segment
    self.assertEqual(len(devices), 3)

  def test_selecting_devices_for_segments_duplicates(self):
    d1 = Device.objects.create(account_key = "123", token = "abc")
    d2 = Device.objects.create(account_key = "123", token = "xyz")
    d3 = Device.objects.create(account_key = "123", token = "ijk")        
    seg1 = Segment.objects.create(name = "Segment 1")
    # d3 is tracking two segments
    seg1.device.add(d1, d2, d3)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    seg2.device.add(d3)
    seg2.save()
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    message.segments.add(seg1, seg2)
    message.save()
    command = SendPushCommand()
    devices = command.get_devices(message)        

    self.assertEqual(len(devices), 3)

  def test_selecting_devices_for_segments_wo_subscribers(self):
    d1 = Device.objects.create(account_key = "123", token = "abc")
    d2 = Device.objects.create(account_key = "123", token = "xyz")
    d3 = Device.objects.create(account_key = "123", token = "ijk")        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg2 = Segment.objects.create(name = "Segment 2")
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    command = SendPushCommand()
    devices = command.get_devices(message)

    self.assertEqual(len(devices), 3)  

  def test_selecting_devices_wo_segments(self):
    d1 = Device.objects.create(account_key = "123", token = "abc")
    d2 = Device.objects.create(account_key = "123", token = "xyz")
    d3 = Device.objects.create(account_key = "123", token = "ijk")        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg1.device.add(d1, d3)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    seg2.device.add(d3)
    seg2.save()
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    message.segments.add(seg1)
    command = SendPushCommand()
    devices = command.get_devices(message)

    self.assertEqual(len(devices), 3)          

  def test_web_service_devices(self):
    d1 = WebServiceDevice.objects.create(account_key = "123", endpoint = "domain.com", subscription_id = "abc", chrome = True)
    d2 = WebServiceDevice.objects.create(account_key = "123", endpoint = "domain.com", subscription_id = "xyz", chrome = True)
    d3 = WebServiceDevice.objects.create(account_key = "123", endpoint = "domain.com", subscription_id = "ijk", chrome = True)
    d4 = WebServiceDevice.objects.create(account_key = "123", endpoint = "domain.com", subscription_id = "ijk", mozilla = True)        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg1.web_service_device.add(d1)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    seg2.web_service_device.add(d3)
    seg2.save()
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    message.segments.add(seg1, seg2)
    message.save()
    command = SendPushCommand()
    devices = command.get_web_service_devices(message, chrome = True)

    self.assertEqual(len(devices), 3)

  def test_web_service_devices_for_segments_duplicates(self):
    d1 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "abc", 
      chrome = True)
    d2 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "xyz", 
      chrome = True)
    d3 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "ijk", 
      chrome = True)
    # Mozilla Device
    d4 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "mno", 
      mozilla = True)        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg1.web_service_device.add(d1, d3, d4)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    seg2.web_service_device.add(d3)
    seg2.save()
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    message.segments.add(seg1, seg2)
    message.save()
    command = SendPushCommand()
    devices = command.get_web_service_devices(message, chrome = True)

    self.assertEqual(len(devices), 3)

  def test_web_service_devices_for_message_wo_segments(self):
    d1 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "abc", 
      chrome = True)
    d2 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "xyz", 
      chrome = True)
    d3 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "ijk", 
      chrome = True)
    # Mozilla
    d4 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "mno", 
      mozilla = True)        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg1.web_service_device.add(d1, d3, d4)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    seg2.web_service_device.add(d3)
    seg2.save()
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    command = SendPushCommand()
    devices = command.get_web_service_devices(message, chrome = True)

    # message has no segments, so all devices are notified
    self.assertEqual(len(devices), 3)

  def test_web_service_devices_wo_segments(self):
    d1 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "abc", 
      chrome = True)
    d2 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "xyz", 
      chrome = True)
    d3 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "ijk", 
      chrome = True)
    # Mozilla
    d4 = WebServiceDevice.objects.create(account_key = "123", 
      endpoint = "domain.com", 
      subscription_id = "mno", 
      mozilla = True)        
    seg1 = Segment.objects.create(name = "Segment 1")
    seg1.web_service_device.add(d1, d3, d4)
    seg1.save()
    seg2 = Segment.objects.create(name = "Segment 2")
    seg2.web_service_device.add(d3)
    seg2.save()
    message = PushMessage.objects.create(title = "title", 
      body = "body", 
      account_key = "123")
    message.segments.add(seg1)
    message.save()        
    command = SendPushCommand()
    devices = command.get_web_service_devices(message, chrome = True)

    self.assertEqual(len(devices), 3)
    self.assertTrue(d2 in devices)

class PushMessageTest(TestCase):

  def tearDown(self):
    # must call .delete() manually for the post_delete hook to clean the created files
    for profile_image in ProfileImage.objects.all():
      profile_image.delete()

  def test_creating_push_message(self):
    image_path = os.path.join(settings.MEDIA_ROOT, 'test', 'image.png')
    pm = PushMessage.objects.create(
      body = "test",
      title = "test title",
      image = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/png')
      )

    self.assertEqual(PushMessage.objects.count(), 1)

  def test_notifications_for_service_worker(self):
    user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    profile = ClientProfile.objects.create(website_push_id = 'web.com.pushmonkey.1', 
      account_key = "abcd", 
      user = user)  
    profile_image_path = os.path.join(settings.MEDIA_ROOT, 'test2', 'image.png')
    profile_image = ProfileImage.objects.create(profile = profile,
      image = SimpleUploadedFile(name='test_image-2.png', content=open(profile_image_path, 'rb').read(), content_type='image/png'))
    image_path = os.path.join(settings.MEDIA_ROOT, 'test', 'image.png')
    pm = PushMessage.objects.create(
      body = "test",
      title = "test title",
      image = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/png'),
      account_key = profile.account_key
      )    
    res = c.get(reverse('service_worker_notifications', args = [pm.account_key]))

    self.assertContains(res, "/media/push_messages")