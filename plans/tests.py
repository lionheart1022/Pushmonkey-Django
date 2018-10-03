from clients.models import ClientProfile, ProfileImage
from clients.tests import create_push_package, clean_push_package_files
from clients.tests import register_user_from_wp, register_user_from_homepage
from datetime import datetime, timedelta
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from models import Plan, mark_payment
from models import PlanVariant as plans
from plans.management.commands.mark_expired import Command
from helpers import create_push_package_for_profile
import json, os
import pushmonkey

c = Client()

class PlansTest(TestCase):

    def tearDown(self):
        for directory in ['test', 'test2']:
            clean_push_package_files(directory)
        for profile_image in ProfileImage.objects.all():
            profile_image.delete()

    def test_payment_processing_not_logged_in(self):
        resp = c.get(reverse('payment_processing', args = [plans.STARTER]))

        self.assertRedirects(resp, reverse('login') + '?next=' + reverse('payment_processing', args = [plans.STARTER]))

    def test_payment_processing_from_wp(self):
        resp_register = register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        logged_in = c.login(username = 'john@gmail.com', password = 'holymomma')
        resp = c.get(reverse('payment_processing', args = [plans.STARTER]))

        self.assertTrue(logged_in)
        self.assertRedirects(resp, profile.return_url + "&push_monkey_package_pending=1&push_monkey_registered=1")

    def test_payment_processing_from_homepage(self):
        resp_register = register_user_from_homepage()
        profile = ClientProfile.objects.all()[0]
        logged_in = c.login(username = 'john@gmail.com', password = 'holymomma')
        resp = c.get(reverse('payment_processing', args = [plans.STARTER]))

        self.assertTrue(logged_in)
        self.assertEqual(resp.status_code, 200)

    def test_pre_expiration_email(self):
        resp_register = register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        plan1 = Plan(user = profile.user, type = plans.TRIAL, end_at = datetime.now() + timedelta(days = 11), status = 'active')
        plan1.save()
        c = Command()
        c.handle()
        subjects = [m.subject for m in mail.outbox]

        self.assertTrue("It's almost that time" in subjects)

    def test_create_fixed_plan(self):
        resp_register = register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        plan = Plan.objects.create_fixed_plan(profile.user)

        self.assertEqual(Plan.objects.all().count(), 1)

    def test_ipn_received_without_push_package(self):
        # sign up a user
        resp = register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        # prepare a push package
        package = create_push_package(os.path.join(settings.MEDIA_ROOT, 'test'))
        # upload icon
        profile_image = ProfileImage(profile = profile)
        image_path = os.path.join(settings.MEDIA_ROOT, 'test', 'image.png')
        profile_image.image = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/png')
        profile_image.save()
        # mock PayPal IPN response
        mock_sender = MockIPNResponse(user_id = profile.user.id, 
            plan_type = plans.PRO, 
            time_units = "M")

        # state before the PayPal IPN Response
        self.assertEqual(pushmonkey.models.PushPackage.objects.count(), 1) 
        self.assertEqual(Plan.objects.count(), 0)
        self.assertFalse(profile.has_push_package())

        # make the PayPal IPN call
        mark_payment(mock_sender)

        # state after the PayPal IPN Response
        self.assertEqual(Plan.objects.count(), 1)
        self.assertEqual(pushmonkey.models.PushPackage.objects.count(), 1)        
        # retrieve the profile from the database again to have the new properties values
        profile = ClientProfile.objects.all()[0]
        self.assertTrue(profile.has_push_package())

    def test_ipn_received_with_push_package(self):
        # sign up a user
        resp = register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        # prepare a push package
        package = create_push_package(os.path.join(settings.MEDIA_ROOT, 'test'))
        # upload icon
        profile_image = ProfileImage(profile = profile)
        image_path = os.path.join(settings.MEDIA_ROOT, 'test', 'image.png')
        profile_image.image = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/png')
        profile_image.save()
        # assign push package to profile
        create_push_package_for_profile(profile)
        # mock PayPal IPN response
        mock_sender = MockIPNResponse(user_id = profile.user.id, 
            plan_type = plans.PRO, 
            time_units = "M")

        # state before the PayPal IPN Response
        self.assertEqual(pushmonkey.models.PushPackage.objects.count(), 1) 
        self.assertEqual(Plan.objects.count(), 0)
        profile = ClientProfile.objects.all()[0]
        self.assertTrue(profile.has_push_package())

        # make the PayPal IPN call
        mark_payment(mock_sender)

        # state after the PayPal IPN Response
        self.assertEqual(Plan.objects.count(), 1)
        self.assertEqual(pushmonkey.models.PushPackage.objects.count(), 1)        
        # retrieve the profile from the database again to have the new properties values
        profile = ClientProfile.objects.all()[0]
        self.assertTrue(profile.has_push_package())


class MockIPNResponse:
    custom = None
    txn_id = '123'
    payment_status = "Completed"

    def __init__(self, **kwargs):
        self.custom = json.dumps(kwargs)

