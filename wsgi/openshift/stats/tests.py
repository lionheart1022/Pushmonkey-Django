from clients.models import ClientProfile
from clients.tests import register_user_from_wp
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from pushmonkey.models import PushMessage

c = Client()

class StatsTest(TestCase):

    def test_url_tracking(self):
        push_message = PushMessage(title = "Title", body = "Body", url_args = "1", account_key = "ABC")
        push_message.save()
        register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        profile.account_key = "ABC"
        profile.save()

        resp = c.get(reverse('track_open', args = [push_message.id]))
        
        self.assertEquals(PushMessage.objects.all().count(), 1)
        self.assertEquals(ClientProfile.objects.all().count(), 1)
        self.assertRedirects(resp, 'http://testwebsite.com?p=1&source=push_monkey')

        profile.url_format_string = 'http://newwebsite.com?p='
        profile.save()

        resp = c.get(reverse('track_open', args = [push_message.id]))

        self.assertRedirects(resp, 'http://newwebsite.com?p=1&source=push_monkey')

    def test_url_tracking_custom_url(self):
        push_message = PushMessage(title = "Title", 
                                   body = "Body", 
                                   url_args = "http://google.com", 
                                   account_key = "ABC", 
                                   custom = True)
        push_message.save()
        register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        profile.account_key = "ABC"
        profile.save()

        resp = c.get(reverse('track_open', args = [push_message.id]))

        self.assertRedirects(resp, 'http://google.com')
