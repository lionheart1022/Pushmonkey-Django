from clients.models import ClientProfile
from contact_messages.forms import MessageForm
from contact_messages.managers import ContactEmailManager
from datetime import datetime, timedelta
from django.conf import settings
from django.core import exceptions
from django.core.mail import send_mail
from django.core.servers.basehttp import FileWrapper 
from django.http import Http404
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from plans.models import Plan
from plans.models import PlanVariant as plans
from plans.models import Prices as prices
from pushmonkey.helpers import is_demo_account, send_demo_notification
from pushmonkey.models import Device, PushMessage, PayloadSafari, PushPackage
from segments.models import Segment
from website_clusters.models import Website
import HTMLParser
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

def home(request):
    message = None
    if request.method == "POST":
        form = MessageForm(data = request.POST)
        print(form)
        if form.is_valid():
            message = form.save()
            manager = ContactEmailManager()
            manager.send_admin_contact(message.email, message.name, message.message)
    else:
        form = MessageForm()
    return render_to_response('home/home.html',
                              {'plans': plans, 'form': form, 'message': message, 'prices': prices},
                              RequestContext(request))

def test(request):
    subprocess.Popen("sleep 10; python /home/django/django_project/manage.py send_push 19936", shell=True)

    title = 'title'
    body = 'body'
    email_address = settings.MANAGERS[0][1]
    subject = 'Push sent: ' + title
    message = 'Body: ' + body
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
              [email_address], fail_silently=False)
    return render_to_response('home/pushed.html')

@csrf_exempt
def push_message(request):
    if request.method != "POST":
        raise Http404
    title = request.POST.get('title', None)
    body = request.POST.get('body', None)
    url_args = request.POST.get('url_args', '')
    account_key = request.POST.get('account_key', None)
    account_keys = request.POST.getlist("account_keys", None)
    scheduled_at = request.POST.get('scheduled_at', None)
    if not scheduled_at or len(scheduled_at) == 0:
        scheduled_at = None
    segments = request.POST.getlist('send_to_segments', None)
    if not segments or len(segments) == 0:
        segments = None
    segments_string = request.POST.get('send_to_segments_string', None)
    if segments_string:
        temp_segments = segments_string.split(",")
        if len(temp_segments):
            segments = temp_segments
    if not title:
        raise Exception("Submitted title is empty. Body: " + body)
    if not body:
        raise Exception("Submitted body is empty. Title: " + title)
    if not account_key and not account_keys:
        raise Exception("Submitted Account Key is empty. Title: " + title)
    if scheduled_at:
        scheduled_at = datetime.strptime(scheduled_at, '%m/%d/%Y %H:%M %p')
    custom = request.POST.get('custom', False)
    if custom:
        custom = True
    image = request.FILES.get('image', None)
    h = HTMLParser.HTMLParser()
    title = h.unescape(title)
    title = title.encode('utf-8', 'ignore').strip(' \n\r')
    truncate_title = lambda data: len(data)>40 and data[:40]+'...' or data
    title = truncate_title(title)
    body = h.unescape(body)
    body = body.encode('utf-8', 'ignore').strip(' \n\r')
    truncate_body = lambda data: len(data)>100 and data[:100]+'...' or data
    body = truncate_body(body)

    should_push = False
    comment = ''
    command_path = settings.SUBPROCESS_COMMAND_PATH
    if account_key:
        try:
            profile = ClientProfile.objects.get(account_key = account_key, status = 'active')
            try:
                plan = Plan.objects.exclude(type = plans.NONE).exclude(status = 'expired').filter(user = profile.user, status = 'active').latest('created_at')
                sent_notifications = PushMessage.objects.sent_notifications_count(account_key = account_key)
                should_push = True
                if sent_notifications >= plan.number_of_notifications:
                    should_push = False
                    comment = 'Notifications number for plan exceeded.'
            except Plan.DoesNotExist:
                comment = 'No price plan for user_id: ' + str(profile.user.id)
        except ClientProfile.DoesNotExist:
            comment = 'No user for this account key or profile is not active.'
        if not should_push:
            try:
                website = Website.objects.get(account_key = account_key)
                comment = ''
                should_push = True
            except Website.DoesNotExist:
                comment = 'No user for this account key or profile is not active or no website cluster.'
        new_message = PushMessage.objects.create(title = title, 
            body = body, 
            url_args = url_args, 
            account_key = account_key, 
            custom = custom, 
            comment = comment, 
            scheduled_at = scheduled_at,
            image = image)
        if segments:
            for segment in Segment.objects.filter(id__in = segments):
                new_message.segments.add(segment)
                new_message.save()
        if should_push and scheduled_at:
            should_push = False
        if should_push:
            # subprocess for async execution 
            subprocess.Popen("sleep 10; python " + command_path + " " + str(new_message.id), shell=True)
    elif account_keys:
        profiles = ClientProfile.objects.filter(account_key__in = account_keys, status = 'active')
        print(profiles)
        for p in profiles:
            notif = PushMessage.objects.create(title = title, 
                    body = body, url_args = url_args, 
                    account_key = p.account_key, custom = custom, 
                    comment = comment, scheduled_at = scheduled_at,
                    image = image)
            print(notif)
            print(notif.id)
            if segments:
                for segment in Segment.objects.filter(id__in = segments):
                    notif.segments.add(segment)
                    notif.save()            
            if not scheduled_at:
                subprocess.Popen("sleep 10; python " + command_path + " " + str(notif.id), shell=True)            
        websites = Website.objects.filter(account_key__in = account_keys)
        for w in websites:
            notif = PushMessage.objects.create(title = title, 
                body = body, url_args = url_args, 
                account_key = w.account_key, custom = custom, 
                comment = comment, scheduled_at = scheduled_at,
                image = image)
            if segments:
                for segment in Segment.objects.filter(id__in = segments):
                    notif.segments.add(segment)
                    notif.save()            
            if not scheduled_at:
                subprocess.Popen("sleep 10; python " + command_path + " " + str(notif.id), shell=True)
    return render_to_response('pushmonkey/pushed.html')

def push(request):
    return render_to_response('home/test.html')

@csrf_exempt
def apn_log(request):
    logger.error("***")
    logger.error(request.POST)
    logger.error(request.POST.get("logs"))
    logger.error("***")    
    return render_to_response('pushmonkey/logged.html')

@csrf_exempt
def apn_push_package(request, website_push_id = ""):
    logger.error("=== apn_push_package")
    if len(website_push_id) == 0:
        raise Exception("Website Push ID can't be empty")
    try:
        push_package = PushPackage.objects.get(website_push_id = website_push_id)
    except:
        push_package = None
    if not push_package:
        #ensure backwards compatibility
        path = os.path.join(settings.STATIC_ROOT, website_push_id, 'pushPackage', 'pushPackage.zip')
        logger.error(path)
        wrapper = FileWrapper(file(path))
        response = StreamingHttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = "attachment; filename=pushPackage.zip"
        response['Content-Length'] = os.path.getsize(path)
        return response
    else:
        logger.error("=== we have a push package")
        path = push_package.path()
        logger.error(path)
        wrapper = FileWrapper(file(path))
        response = StreamingHttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = "attachment; filename=pushPackage.zip"
        response['Content-Length'] = os.path.getsize(path)
        return response 
    raise Http404

@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def apn_device_register(request, device_id="0", website_id=""):
    if request.method == "POST":
        account_key = None
        try:
            push_package = PushPackage.objects.get(website_push_id = website_id)
        except:
            push_package = None
        if push_package:
            new_device = Device(token = device_id, account_key = push_package.identifier)
        else:
            # the old system, w/o push packages
            profile = None
            account_key = None
            try:
                profile = ClientProfile.objects.get(website_push_id = website_id)
                account_key = profile.account_key
            except ClientProfile.DoesNotExist:
                if website_id == 'web.robthomas.fsm':
                    profile = ClientProfile.objects.get(website_push_id = 'web.com.pushmonkey.VXLDZNEQSGI0J981C')
                    account_key = profile.account_key
            if not account_key:
                try:
                    website = Website.objects.get(account_key = push_package.identifier)
                    account_key = website.account_key
                except Website.DoesNotExist:
                    raise Exception('No profile or website found for ' + website_id)
            new_device = Device(token = device_id, account_key = account_key)
        new_device.save()
        if new_device.id is not None:
            
            if is_demo_account(account_key):
                send_demo_notification(account_key)
        else:
            raise Exception("The device id didn't save " + device_id)
    elif request.method == "DELETE":
        account_key = None
        try:
            push_package = PushPackage.objects.get(website_push_id = website_id)
        except:
            push_package = None
        if push_package:
            account_key = push_package.identifier
        else:
            # the old system, w/o push packages
            profile = None
            try:
                profile = ClientProfile.objects.get(website_push_id = website_id)
            except ClientProfile.DoesNotExist:
                if website_id == 'web.robthomas.fsm':
                    profile = ClientProfile.objects.get(website_push_id = 'web.com.pushmonkey.VXLDZNEQSGI0J981C')
            account_key = profile.account_key
            if not profile:
                raise Exception('No profile found for ' + website_id)
        old_devices = Device.objects.filter(token__exact=device_id, account_key = account_key)
        for device in old_devices:
            device.delete()
    return render_to_response('pushmonkey/registered.html')

def daily_digest_cron(request):
    yesterday = datetime.today() - timedelta(1)
    y_day = yesterday.day
    y_month = yesterday.month
    y_year = yesterday.year
    pms = PushMessage.objects.filter(created_at__day = y_day, created_at__month = y_month, created_at__year = y_year)
    text = "Stats for Safari Push Messages Sent on " + str(yesterday) + "\n" 
    text += "=====\n"
    for pm in pms:
        text += "Title: " + pm.title + "\n"
        text += "Body: " + pm.body + "\n"
        text += "Number of subscribers: " + pm.device_num + "\n"
        text += "===\n"
    emails = [person[1] for person in settings.MANAGERS]
    subject = "Push Notification Stats from " + yesterday.strftime('%d, %b %Y')
    send_mail(subject, text, settings.EMAIL_HOST_USER, emails, fail_silently=False)
    return render_to_response('pushmonkey/cron.html')

def server_error(request):
    return render_to_response('500.html', 
                              RequestContext(request))