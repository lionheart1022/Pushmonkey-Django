from django.test import TestCase
from django.contrib.auth.models import User
from models import Website, WebsiteCluster
from helpers import clean_website_url

class WebsiteClusterTest(TestCase):

    def test_clean_website_url(self):

    	user = User.objects.create_user(username = "a", password = 'b')
    	user.save()

    	cluster = WebsiteCluster(creator = user)
    	cluster.save()

    	website = Website(website_url = "http://website.com/", cluster = cluster)
    	website.save()

        variants = [
        "http://website.com",
        "https://website.com/",
        ]

        for variant in variants:
        	clean = clean_website_url(variant)
        	website = Website.objects.get(website_url__contains = clean)
        	self.assertTrue(website is not None)


