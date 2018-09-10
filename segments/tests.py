from clients.models import ClientProfile
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from models import Segment
from pushmonkey.models import Device, WebServiceDevice
import json

c = Client()

class SegmetsTests(TestCase):

    def test_retrieving_segments(self):

      user = User.objects.create_user('john', 
        'lennon@thebeatles.com', 
        'johnpassword')
      profile = ClientProfile.objects.create(
        website_push_id = 'web.com.pushmonkey.1', 
        user = user)
      seg1 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 1")
      seg2 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 2")
      data = {"endpoint": "xyz"}
      res = c.post(reverse('segments', args = ["abc"]), data)
      json_res = json.loads(res.content)

      self.assertEqual(len(json_res["segments"]), 2)
      self.assertContains(res, "Seg 2")
      self.assertContains(res, "<h3")

    def test_saving_segments_for_safari(self):
      user = User.objects.create_user('john', 
        'lennon@thebeatles.com', 
        'johnpassword')
      profile = ClientProfile.objects.create(
        website_push_id = 'web.com.pushmonkey.1', 
        user = user)
      seg1 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 1")
      seg2 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 2")
      device = Device.objects.create(token = "123456", account_key = "abc")
      data = {"segments[]": [seg1.id, seg2.id], "token": "123456"}
      res = c.post(reverse('save_segments', args = ["abc"]), data)

      self.assertEqual(Segment.objects.get(id = seg1.id).device.count(), 1)
      self.assertEqual(Segment.objects.get(id = seg2.id).device.count(), 1)
      self.assertContains(res, "ok")

    def test_saving_segments_for_chrome(self):
      user = User.objects.create_user('john', 
        'lennon@thebeatles.com', 
        'johnpassword')
      profile = ClientProfile.objects.create(
        website_push_id = 'web.com.pushmonkey.1', 
        user = user)
      seg1 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 1")
      seg2 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 2")
      device = WebServiceDevice.objects.create(endpoint = "domain.com", 
        account_key = "abc",
        subscription_id = "123456")
      data = {"segments[]": [seg1.id, seg2.id], "token": "domain.com/123456"}
      res = c.post(reverse('save_segments', args = ["abc"]), data)

      self.assertContains(res, "ok")
      self.assertEqual(Segment.objects.get(id = seg1.id).web_service_device.count(), 1)
      self.assertEqual(Segment.objects.get(id = seg2.id).web_service_device.count(), 1)

    def test_saving_segments_for_chrome_no_token(self):
      user = User.objects.create_user('john', 
        'lennon@thebeatles.com', 
        'johnpassword')
      profile = ClientProfile.objects.create(
        website_push_id = 'web.com.pushmonkey.1', 
        user = user)
      seg1 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 1")
      seg2 = Segment.objects.create(account_key = "abc", client = profile, name = "Seg 2")
      device = WebServiceDevice.objects.create(endpoint = "123456", account_key = "abc")
      data = {"segments[]": [seg1.id, seg2.id], "token": ""}
      res = c.post(reverse('save_segments', args = ["abc"]), data)

      self.assertEqual(Segment.objects.get(id = seg1.id).web_service_device.count(), 0)
      self.assertEqual(Segment.objects.get(id = seg2.id).web_service_device.count(), 0)
      self.assertContains(res, "no token")  

    def test_creating_segments(self):

      user = User.objects.create_user('john', 
        'lennon@thebeatles.com', 
        'johnpassword')
      profile = ClientProfile.objects.create(
        website_push_id = 'web.com.pushmonkey.1', 
        account_key = "abc",
        user = user)

      data = {"name": "Boxing"}
      res = c.post(reverse('create_segment', args = ["abc"]), data)

      self.assertEqual(Segment.objects.count(), 1)
      self.assertContains(res, "ok")  

    def test_deleting_segments(self):

      user = User.objects.create_user('john', 
        'lennon@thebeatles.com', 
        'johnpassword')
      profile = ClientProfile.objects.create(
        website_push_id = 'web.com.pushmonkey.1', 
        account_key = "abc",
        user = user)
      s = Segment.objects.create(account_key = "abc")

      data = {"id": s.id}
      res = c.post(reverse('delete_segment', args = ["abc"]), data)

      self.assertEqual(Segment.objects.count(), 0)
      self.assertContains(res, "ok")  