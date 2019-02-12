from clients.models import ClientProfile, ProfileImage
from models import Website

def website_from_profile(profile, cluster):
	website = Website(
		account_key = profile.account_key, 
		return_url = profile.return_url, 
		website_name = profile.website_name,
		website_url = profile.website,
		cluster = cluster
		)
	website.save()
	return website

def clean_website_url(website_url):
	clean = website_url
	if clean.startswith('https://'):
		clean = website_url[len('https://'):]
	elif clean.startswith('http://'):
		clean = website_url[len('http://'):]
	if clean.endswith('/'):
		clean = clean[0:len(clean)-1]
	return clean

def profile_for_cluster(cluster):
	profile = ClientProfile.objects.get(user = cluster.creator)
	return profile

def profile_image_for_profile(profile):
	profile_image = ProfileImage.objects.get(profile = profile)
	return profile_image

def profile_image_for_cluster(cluster):
	profile = profile_for_cluster(cluster)
	return profile_image_for_profile(profile)