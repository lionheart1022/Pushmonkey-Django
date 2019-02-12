from clients.models import ClientProfile
from contact_messages.forms import MessageForm
from contact_messages.managers import ContactEmailManager
from datetime import datetime, timedelta
from django.conf import settings
from django.core import exceptions
from django.core.mail import send_mail
from django.core.servers.basehttp import FileWrapper 
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from plans.models import Plan
from plans.models import PlanVariant as plans
from plans.models import Prices as prices
from pushmonkey.models import Device, PushMessage, PayloadSafari, PushPackage
from website_clusters.models import Website
import HTMLParser
import os
import subprocess

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
    subprocess.Popen("sleep 10; python /var/lib/openshift/" + settings.OPENSHIFT_ID + "/app-root/runtime/repo/wsgi/openshift/manage.py send_push 1", shell=True)

    title = 'title'
    body = 'body'
    email_address = settings.MANAGERS[0][1]
    subject = 'Push sent: ' + title
    message = 'Body: ' + body
    send_mail(subject, message, settings.EMAIL_HOST_USER,
              [email_address], fail_silently=False)
    return render_to_response('home/home.html')

@csrf_exempt
def push_message(request):
    if request.method != "POST":
        raise Http404
    title = ''
    if request.POST.has_key('title'):
        title = request.POST['title']
    body = ''
    if request.POST.has_key('body'):
        body = request.POST['body']
    url_args = ''
    if request.POST.has_key('url_args'):
        url_args = request.POST['url_args']
    account_key = ''
    if request.POST.has_key('account_key'):
        account_key = request.POST['account_key']
    if not len(title):
        raise Exception("Submitted title is empty. Body: " + body)
    if not len(body):
        raise Exception("Submitted body is empty. Title: " + title)
    if not len(account_key):
        raise Exception("Submitted Account Key is empty. Title: " + title)
    custom = request.POST.get('custom', False)
    if custom:
        custom = True
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
        except Website.DoesNotExist:
            comment = 'No user for this account key or profile is not active or no website cluster.'

    new_message = PushMessage(title = title, body = body, url_args = url_args, 
                              account_key = account_key, custom = custom, comment = comment)
    new_message.save();

    if should_push:
        # subprocess for async execution
        command_path = "/var/lib/openshift/" + settings.OPENSHIFT_ID + "/app-root/runtime/repo/wsgi/openshift/manage.py send_push" 
        message_id = new_message.id
        subprocess.Popen("sleep 10; python " + command_path + " " + str(message_id), shell=True)

    return render_to_response('pushmonkey/pushed.html')

def push(request):
    return render_to_response('home/test.html')

@csrf_exempt
def apn_log(request):
    print "***"
    print request.POST
    return render_to_response('pushmonkey/logged.html')

@csrf_exempt
def apn_push_package(request, website_push_id = ""):
    if len(website_push_id) == 0:
        raise Exception("Website Push ID can't be empty")
    try:
        push_package = PushPackage.objects.get(website_push_id = website_push_id)
    except:
        push_package = None
    if not push_package:
        #ensure backwards compatibility
        path = os.path.join(settings.STATIC_ROOT, website_push_id, 'pushPackage', 'pushPackage.zip')
        wrapper = FileWrapper(file(path))
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Length'] = os.path.getsize(path)
        return response 
    else:
        path = push_package.path()
        wrapper = FileWrapper(file(path))
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Length'] = os.path.getsize(path)
        return response 
    raise Http404

@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def apn_device_register(request, device_id="0", website_id=""):
    if request.method == "POST":
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
            pass
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
