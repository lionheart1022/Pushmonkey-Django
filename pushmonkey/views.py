from clients.models import ClientProfile
from clients.models import ClientProfile, ProfileImage
from django.conf import settings
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from helpers import is_demo_account, send_demo_notification
from pushmonkey.models import PushMessage, Device, WebServiceDevice
from website_clusters.models import Website
import json

GCM_ENDPOINT = "https://android.googleapis.com/gcm/send"
MOZ_ENDPOINT = "https://updates.push.services.mozilla.com/wpush/v1"

@csrf_exempt
def notifications(request, account_key = None):
	
	if not account_key:

		raise Http404
	message = PushMessage.objects.filter(account_key = account_key).order_by('-created_at')[0]
	if not message:

		raise Http404
	profile = ClientProfile.objects.get(account_key = account_key)
	profile_image = ProfileImage.objects.get(profile = profile)
	response_data = {
		"body": message.body,
		"icon": "https://" + request.META.get('HTTP_HOST', 'example.com') + profile_image.image128.url,
		"title": message.title,
		"id": message.id
	}
	if message.image:
		response_data["image"] = message.image.url
	return HttpResponse(json.dumps(response_data), content_type = "application/json")

@csrf_exempt
def register(request, account_key = None):
	if not account_key:

		raise Http404
	endpoint = request.POST.get('endpoint', False)
	if not endpoint:

		raise Http404
	subscription_id = endpoint.split("/")[-1]
	endpoint = endpoint.replace("/%s" % subscription_id, '')
	is_chrome = (endpoint == GCM_ENDPOINT)
	is_mozilla = (endpoint == MOZ_ENDPOINT)
	d = WebServiceDevice(account_key = account_key,
		endpoint = endpoint, 
		subscription_id = subscription_id,
		chrome = is_chrome,
		mozilla = is_mozilla)
	d.save()
	if is_demo_account(account_key):
		send_demo_notification(account_key)
		d.is_test_device = True
		d.save()
	response_data = {"response": "ok"}
	return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def unregister(request, subscription_id = None):
	if not subscription_id:

		raise Http404
	s = WebServiceDevice.objects.filter(subscription_id = subscription_id)
	s.delete()
	response_data = {"response": "ok"}
	return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def resend_demo(request, account_key = None):
	if not account_key:

		raise Http404
	if not is_demo_account(account_key):

		raise Http404
	endpoint = request.POST.get('endpoint', False)
	if not endpoint:

		raise Http404
	subscription_id = endpoint.split("/")[-1]
	endpoint = endpoint.replace("/%s" % subscription_id, '')
	d = WebServiceDevice.objects.filter(
		account_key = account_key, 
		subscription_id = subscription_id).first()
	d.tested = False
	d.save()
	send_demo_notification(account_key)
	response_data = {"response": "ok"}
	return HttpResponse(json.dumps(response_data), content_type="application/json")	

@xframe_options_exempt
def service_worker(request, account_key = None):
	if not account_key:

		raise Http404
	rendered = render_to_string('pushmonkey/service_worker.js', {'account_key': account_key})
	return HttpResponse(rendered, content_type="application/javascript")

@xframe_options_exempt
def manifest(request, account_key = None):
	if not account_key:

		raise Http404
	rendered = render_to_string('pushmonkey/manifest.json', {})
	return HttpResponse(rendered, content_type="application/json")

@xframe_options_exempt
def register_service_worker(request, account_key = None):
	if not account_key:

		raise Http404	
	rendered = render_to_string('pushmonkey/register_service_worker.html', {"account_key": account_key})
	return HttpResponse(rendered)

@xframe_options_exempt
def config_js(request, account_key = None):
	if not account_key:

		raise Http404
	is_not_wordpress = request.GET.get("not_wp", 0)
	is_demo = {True: 1, False: 0}[is_demo_account(account_key)]
	dialog_color = request.GET.get("dialog_color", settings.DEFAULT_DIALOG_BACKGROUND)
	button_color = request.GET.get("button_color", settings.DEFAULT_DIALOG_BUTTON)
	rendered = render_to_string('pushmonkey/config.js', {
		"account_key": account_key,
		"dialog_color": dialog_color,
		"button_color": button_color,
		"is_demo": is_demo,
		"is_not_wordpress": int(is_not_wordpress)
		})
	return HttpResponse(rendered, content_type="application/json")

@xframe_options_exempt
def sdk_js(request, account_key = None):
	if not account_key:

		raise Http404
	# is_demo = {True: 1, False: 0}[is_demo_account(account_key)]
	is_demo = 0
	try:
		profile = ClientProfile.objects.get(account_key = account_key)
		subdomain = profile.subdomain
	except ClientProfile.DoesNotExist:
		try: 
			website = Website.objects.get(account_key = account_key)
			subdomain = website.subdomain
		except Website.DoesNotExist:
			raise Http404
	rendered = render_to_string('pushmonkey/sdk.js', {
		"account_key": account_key,
		"subdomain": subdomain,
		"is_demo": is_demo
		})
	return HttpResponse(rendered, content_type="application/json")