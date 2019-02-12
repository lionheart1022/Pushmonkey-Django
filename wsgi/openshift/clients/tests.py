from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from models import ClientProfile, ProfileImage
from plans.models import Plan, PlanVariant
from pushmonkey.models import PushPackage
from website_clusters.models import WebsiteCluster, Website, WebsiteIcon
import os
import shutil
import urllib

c = Client()

class RegistrationTest(TestCase):

    def tearDown(self):
        for directory in ['test', 'test2']:
            clean_push_package_files(directory)
        # must call .delete() manually for the post_delete hook to clean the created files
        for icon in WebsiteIcon.objects.all():
            icon.delete()
        for profile_image in ProfileImage.objects.all():
            profile_image.delete()

    def test_registration(self):
        response = c.get(reverse('register'))

        self.assertEqual(response.status_code, 200)

    def test_registration_from_wp_get(self):
        d = {
            'registering': 1,
            'first_name': 'John', 
            'email': 'john@gmail.com',
            'websiteName': 'Test Website',
            'websiteURL': 'http://testwebsite.com',
            'returnURL': 'http://testwebsite.com?page=1'
        }
        response = c.get(reverse('register') + '?' + urllib.urlencode(d))

        self.assertEqual(response.status_code, 200)

    def test_registration_from_wp_post(self):
        response = register_user_from_wp()
        profiles = ClientProfile.objects.all()
        subjects = [m.subject for m in mail.outbox]
        subject = "Capt'n, john@gmail.com signed up."

        self.assertRedirects(response, reverse('customise') + '?profile_id=1')
        self.assertEqual(profiles.count(), 1)
        self.assertTrue(subject in subjects)
        self.assertEqual(len(subjects), 2)

    def test_registration_thank_you_from_wp(self):
        register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        resp = c.get(reverse('register_thank_you', args = [profile.id]))

        self.assertRedirects(resp, profile.return_url + '&push_monkey_package_pending=1&push_monkey_registered=1')

    def test_registration_from_homepage_get(self):
        d = {
            'websiteURL': 'http://fromhome.com',
            'email': 'home@gmail.com'
        }
        resp = c.get(reverse('register') + '?' + urllib.urlencode(d))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, d['email'])

    def test_registration_from_homepage_post(self):
        resp = register_user_from_homepage()
        profiles = ClientProfile.objects.all()
        subjects = [m.subject for m in mail.outbox]
        subject = "Capt'n, john@gmail.com signed up."

        self.assertRedirects(resp, reverse('customise') + '?profile_id=1')
        self.assertEqual(profiles.count(), 1)
        self.assertTrue(subject in subjects)
        self.assertEqual(len(subjects), 2)

    def test_registration_thank_you_from_homepage(self):
        register_user_from_homepage()
        profile = ClientProfile.objects.all()[0]
        resp = c.get(reverse('register_thank_you', args = [profile.id]))

        self.assertEqual(resp.status_code, 200)
        templates = [t.name for t in resp.templates]
        self.assertTrue('clients/register-thank-you.html' in templates)

    def test_api_get_plan_name_no_plan(self):
        register_user_from_homepage()
        profile = ClientProfile.objects.all()[0]
        profile.account_key = "123"
        profile.save()
        resp = c.post(reverse('api_get_plan_name'), {
            'account_key': "123"
        })

        self.assertContains(resp, "No price plan")
        self.assertEqual(resp.status_code, 200)

    def test_registration_from_homepage_post_without_http(self):
        resp = register_user_without_http()
        profiles = ClientProfile.objects.all()
        subjects = [m.subject for m in mail.outbox]
        subject = "Capt'n, john@gmail.com signed up."

        self.assertContains(resp, 'errorlist')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(subject in subjects)

    def test_registration_from_wp_envato_get(self):
        d = {
            'registering': 1,
            'first_name': 'John', 
            'email': 'john@gmail.com',
            'websiteName': 'Test Website',
            'websiteURL': 'http://testwebsite.com',
            'returnURL': 'http://testwebsite.com?page=1',
            'envato': 1,
        }
        resp = c.get(reverse('register') + '?' + urllib.urlencode(d))
        
        self.assertTrue(resp.context['profile_form'].initial['from_envato'])
        self.assertEqual(resp.status_code, 200)

    def test_registration_from_wp_envato_post(self):
        resp = register_user_from_wp_envato()
        profiles = ClientProfile.objects.all()
        subjects = [m.subject for m in mail.outbox]
        subject = "Capt'n, john@gmail.com signed up."

        self.assertRedirects(resp, reverse('customise') + '?profile_id=1')
        self.assertEqual(profiles.count(), 1)
        self.assertTrue(subject in subjects)
        self.assertEqual(len(subjects), 2)

    def test_api_get_plan_name(self):
        register_user_from_homepage()
        profile = ClientProfile.objects.all()[0]
        profile.account_key = "123"
        profile.save()
        plan = Plan(user = profile.user, type="1", status="active")
        plan.save()
        resp = c.post(reverse('api_get_plan_name'), {
            'account_key': "1234"
        })

        self.assertContains(resp, "error")
        self.assertEqual(resp.status_code, 200)

    def test_customise(self):
        register_user_from_homepage()
        profile = ClientProfile.objects.all()[0]
        resp = c.post(reverse('customise') + '?profile_id=' + str(profile.id), {
            'profile_id': profile.id,
            'website_url': 'www.feelings.com',
            'website_name': 'Feelings'
        })
        new_profile = ClientProfile.objects.all()[0]
        self.assertRedirects(resp, reverse('overview', args = [profile.id]))
        self.assertEqual(str(new_profile.website), str('http://www.feelings.com/'))

    def test_transition_from_trial_to_fixed_price(self):
        """
        This works only after the Trial has expired.
        """
        # create a new client
        resp = register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        profile.account_key = "123"
        profile.save()
        resp = c.get(reverse('register_thank_you', args = [profile.id]))
        # make profile active after accessing register_thank_you, because register_thank_you redirects 
        # active profiles.
        profile.status = 'active'
        profile.save()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Plan.objects.count(), 1)

        # make the current plan expired
        plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(profile.user)
        self.assertFalse(has_only_expired_plans)
        plan.status = 'expired'
        plan.save()
        plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(profile.user)
        self.assertTrue(has_only_expired_plans)

        # sign in and convert to fixed priced
        resp = c.post(reverse('api_sign_in'), {
            'api_token': 'john@gmail.com', 
            'api_secret': 'holymomma',
            'envato': True,
            })

        self.assertContains(resp, "signed_in")
        self.assertContains(resp, "transitioned_to_envato")
        self.assertEqual(Plan.objects.all().count(), 2)

    def test_go_pro_from_wp(self):

        #
        # pre-requisites for fully signed up client
        # 
        package = create_push_package(os.path.join(settings.MEDIA_ROOT, 'test'))
        # register
        resp = register_user_from_wp()
        profile = ClientProfile.objects.all()[0]
        # upload icon
        profile_image = ProfileImage(profile = profile)
        image_path = os.path.join(settings.MEDIA_ROOT, 'test', 'image.png')
        profile_image.image = SimpleUploadedFile(name='test_image.png', content=open(image_path, 'rb').read(), content_type='image/png')
        profile_image.save()
        # select plan
        resp = c.get(reverse('register_thank_you', args = [profile.id]))
        profile = ClientProfile.objects.all()[0]
        profile.status = 'active'
        profile.save()
        plan = Plan.objects.all()[0]
        package = PushPackage.objects.all()[0]

        # assertions for fully signed up client
        self.assertEqual(profile.status, 'active')
        self.assertEqual(ClientProfile.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 1)
        self.assertEqual(plan.type, PlanVariant.TRIAL)
        self.assertEqual(PushPackage.objects.count(), 1)
        self.assertTrue(package.used)

        # convert plan to Pro. 
        # ! This workflow is not 100% in accordance to the website, because 
        # the client would select directly the Pro plan, without having a Trial plan first
        plan.type = PlanVariant.PRO
        plan.save()

        # sign in from WordPress, from old version of plugin
        resp = c.post(reverse('api_sign_in'), {
            'api_token': 'john@gmail.com', 
            'api_secret': 'holymomma',
            })

        # assertions for successfully signing in
        self.assertContains(resp, "signed_in")
        self.assertContains(resp, package.identifier)
        self.assertContains(resp, profile.user.email)
        self.assertContains(resp, "log")

        # assert that website cluster exists
        self.assertEqual(WebsiteCluster.objects.count(), 1)
        cluster = WebsiteCluster.objects.all()[0]
        self.assertEqual(cluster.website_set.count(), 1)

        # sign in from WordPress, from new version of plugin from the website registered with
        resp = c.post(reverse('api_sign_in'), {
            'api_token': 'john@gmail.com', 
            'api_secret': 'holymomma',
            'website_url': 'http://testwebsite.com',
            })

        # assertions for existing website in cluster
        self.assertNotContains(resp, "log")
        self.assertContains(resp, profile.account_key)
        self.assertContains(resp, package.identifier)

        # sign in from WordPress, from new version of plugin from a new website
        resp = c.post(reverse('api_sign_in'), {
            'api_token': 'john@gmail.com', 
            'api_secret': 'holymomma',
            'website_url': 'http://testwebsite2.com',
            })
        self.assertContains(resp, "log")
        self.assertContains(resp, profile.account_key)

        # create a new website in the cluster (done from getpushmonkey.com Dashboard)
        website = Website(
            cluster = cluster, 
            return_url = "http://testwebsite2.com/wp-admin/index.php", 
            website_name = "Test Website 2",
            website_url = "http://testwebsite2.com")
        package2 = create_push_package(os.path.join(settings.MEDIA_ROOT, 'test2'))
        website.account_key = package2.identifier
        website.save()

        self.assertEqual(cluster.website_set.count(), 2)

        # sign in AGAIN from WordPress, from new version of plugin from a new website
        resp = c.post(reverse('api_sign_in'), {
            'api_token': 'john@gmail.com', 
            'api_secret': 'holymomma',
            'website_url': 'http://testwebsite2.com',
            })
        self.assertNotContains(resp, "log")
        self.assertContains(resp, website.account_key)
        self.assertNotContains(resp, profile.account_key)

        # sign in from getpushmonkey.com
        #
        # TODO:
        #

    def test_website_adding_get(self):
        # create and log in a user
        register_user_from_homepage()
        logged_in = c.login(username = 'john@gmail.com', password = 'holymomma')
        profile = ClientProfile.objects.all()[0]
        plan = Plan(user = profile.user, type = PlanVariant.PRO, status = 'active')
        plan.save()
        # assert that he logged in
        self.assertTrue(logged_in)

        resp = c.get(reverse('websites'))
        self.assertEqual(resp.status_code, 200)

    def test_website_adding_post(self):
        # create a push package
        package = create_push_package(os.path.join(settings.MEDIA_ROOT, 'test2'))
        # create and log in a user
        register_user_from_homepage()
        logged_in = c.login(username = 'john@gmail.com', password = 'holymomma')
        profile = ClientProfile.objects.all()[0]
        # add an account_key because the test will not actually associate a push 
        # package to this profile
        profile.account_key = "123"
        profile.save()
        plan = Plan(user = profile.user, type = PlanVariant.PRO, status = 'active')
        plan.save()
        # assert that he logged in
        self.assertTrue(logged_in)
        self.assertEqual(WebsiteIcon.objects.count(), 0)

        # get the URL first, to create the website cluster
        resp = c.get(reverse('websites'))
        self.assertEqual(resp.status_code, 200)

        # fill in the form
        icon_file = open(os.path.join(settings.MEDIA_ROOT, 'test2', 'image.png'))
        resp = c.post(reverse('websites'), {
            'website_url': 'http://test2.com', 
            'icon': icon_file, 
            'website_name': "Ze Test",
            })

        # assert that websites have been created
        self.assertRedirects(resp, reverse('websites'))
        self.assertEqual(WebsiteIcon.objects.count(), 1)
        self.assertEqual(WebsiteCluster.objects.count(), 1)
        cluster = WebsiteCluster.objects.all()[0]
        self.assertEqual(cluster.website_set.count(), 2)
        for website in cluster.website_set.all():
            self.assertTrue(website.account_key != None)
        self.assertEqual(cluster.website_set.filter(account_key = package.identifier).count(), 1)

def register_user_from_wp():
    resp = c.post(reverse('register') + '?registering=1', {
        'first_name': 'John', 
        'email': 'john@gmail.com',
        'password': 'holymomma',
        'password_confirm': 'holymomma',
        'website_name': 'Test Website',
        'website': 'http://testwebsite.com',
        'return_url': 'http://testwebsite.com?page=admin'
    })
    return resp

def register_user_from_wp_envato():
    resp = c.post(reverse('register') + '?registering=1', {
        'first_name': 'John', 
        'email': 'john@gmail.com',
        'password': 'holymomma',
        'password_confirm': 'holymomma',
        'website_name': 'Test Website',
        'website': 'http://testwebsite.com',
        'return_url': 'http://testwebsite.com?page=admin',
        'from_envato': True
    })
    return resp

def register_user_from_homepage():
    resp = c.post(reverse('register'), {
        'first_name': 'John', 
        'email': 'john@gmail.com',
        'password': 'holymomma',
        'password_confirm': 'holymomma',
        'website': 'http://fromhome.com',
    })
    return resp

def register_user_without_http():
    resp = c.post(reverse('register'), {
        'first_name': 'John', 
        'email': 'john@gmail.com',
        'password': 'holymomma',
        'password_confirm': 'holymomma',
        'website': 'www.fromhome.com',
    })
    return resp

def create_push_package(path):
    package = PushPackage(website_push_id_created = True)
    package.key_pem = os.path.join(path, 'key.pem')
    package.cert_pem = os.path.join(path, 'cert.pem')
    package.cert_p12 = os.path.join(path, 'cert.p12')
    package.website_push_id_created = True
    package.save()
    return package

def clean_push_package_files(path):
    website_json_path = os.path.join(settings.MEDIA_ROOT, path, 'website.json')
    if os.path.exists(website_json_path):
        os.remove(website_json_path)
    push_package_path = os.path.join(settings.MEDIA_ROOT, path, 'pushPackage.zip')
    if os.path.exists(push_package_path):
        os.remove(push_package_path)
    iconset_path = os.path.join(settings.MEDIA_ROOT, path, 'iconset')
    if os.path.exists(iconset_path) and os.path.isdir(iconset_path):
        shutil.rmtree(iconset_path)
