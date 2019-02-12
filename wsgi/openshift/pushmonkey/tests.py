from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from clients.models import ClientProfile
from models import PushPackage, Device
from managers import PushPackageManager

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
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        profile = ClientProfile(website_push_id = 'web.com.pushmonkey.1', user = user)
        profile.save()
        response = c.post(reverse('apn_device_register', args = ["ABC", 'web.com.pushmonkey.1']))
        added_devices_count = Device.objects.all().count()
        resp = c.delete(reverse('apn_device_register', args = ["ABC", 'web.com.pushmonkey.1']))
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
        response = c.post(reverse('apn_device_register', args = ["ABC", 'web.com.pushmonkey.1']))
        added_devices_count = Device.objects.all().count()
        resp = c.delete(reverse('apn_device_register', args = ["ABC", 'web.com.pushmonkey.1']))
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
