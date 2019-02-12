from pushmonkey.managers import PushPackageManager
import clients

def get_profile_for_user_id(user_id):
	try:
		profile = clients.models.ClientProfile.objects.get(user__id = user_id)
		return profile
	except:
		return None

def create_push_package_for_profile(profile):
	if profile.has_push_package():
		return None
	package_manager = PushPackageManager()
	package = package_manager.get_push_package(profile)
	if package:
		profile_image = clients.models.ProfileImage.objects.get(profile = profile)
		package.generate_zip(profile.website_name, 
							profile.website,
							profile_image.image128_2x.path,
							profile_image.image128.path,
							profile_image.image32_2x.path,
							profile_image.image32.path,
							profile_image.image16_2x.path,
							profile_image.image16.path,
							)
		profile.status = 'active'
		profile.account_key = package.identifier
		profile.website_push_id = package.website_push_id
		profile.save()
		package.used = True
		package.save()
	return package