from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.clickjacking import xframe_options_exempt
from pushmonkey.models import PushMessage, Device, WebServiceDevice
from clients.models import ClientProfile
from datetime import datetime, timedelta
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from plans.models import Plan
from django.views.decorators.csrf import csrf_exempt
import random
import json

@xframe_options_exempt
def stats(request, account_key = None):
    should_show_placeholder = False
    if not account_key:
        should_show_placeholder = True

    notifications = PushMessage.objects.filter(account_key = account_key).count()
    #notifications = 783
    subscribers = Device.objects.filter(account_key = account_key).count()
    subscribers += WebServiceDevice.objects.filter(account_key = account_key).count()
    #subscribers = 2341
    sent_notifications = PushMessage.objects.sent_notifications_count(account_key = account_key)
    #sent_notifications = 130000
    number_of_days = 7
    if request.GET.has_key('number_of_days'):
        number_of_days = int(request.GET['number_of_days'])
    sent_notifications_dataset, opened_notifications_dataset = \
            PushMessage.objects.sent_and_opened_datasets(number_of_days = number_of_days, 
                                                         account_key = account_key)
    #sent_notifications_dataset = [random.randint(60, 100) for i in range(0, number_of_days)]
    #opened_notifications_dataset = [random.randint(30, 60) for i in range(0, number_of_days)]
    labels_dataset = PushMessage.objects.labels_dataset(number_of_days = number_of_days)
    
    plan = None
    if account_key:
        profile = ClientProfile.objects.get(account_key = account_key)
        plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(profile.user)

    remaining_notifications = 0
    if plan:
        remaining_notifications = plan.number_of_notifications - sent_notifications
    #remaining_notifications = 50000

    return render_to_response('stats/stats.html', 
                              {
                                  'should_show_placeholder': should_show_placeholder,
                                  'notifications':notifications, 
                                  'subscribers': subscribers, 
                                  'sent_notifications_dataset': sent_notifications_dataset,
                                  'opened_notifications_dataset': opened_notifications_dataset,
                                  'labels_dataset': labels_dataset,
                                  'sent_notifications': sent_notifications,
                                  'remaining_notifications': remaining_notifications,
                              }, 
                              RequestContext(request))

@csrf_exempt
def stats_api(request):
    print request.POST
    account_key = request.POST.get('account_key', None)
    if not account_key:
        response_data = {'Error': 'Wrong Account Key'}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    subscribers = Device.objects.filter(account_key = account_key).count()
    subscribers += WebServiceDevice.objects.filter(account_key = account_key).count()
    notifications = PushMessage.objects.filter(account_key = account_key).count()
    number_of_days = 7
    if request.GET.has_key('number_of_days'):
        number_of_days = int(request.GET['number_of_days'])
    sent_notifications_dataset, opened_notifications_dataset = \
            PushMessage.objects.sent_and_opened_datasets(number_of_days = number_of_days, 
                                                         account_key = account_key)
    labels_dataset = PushMessage.objects.labels_dataset(number_of_days = number_of_days)
    sent_notifications = PushMessage.objects.sent_notifications_count(account_key = account_key)
    plan = None
    if account_key:
        try:
            profile = ClientProfile.objects.get(account_key = account_key)
            plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(profile.user)
        except ClientProfile.DoesNotExist:
            profile = None
    remaining_notifications = 0
    if plan:
        remaining_notifications = plan.number_of_notifications - sent_notifications
    response_data = {
        'subscribers': subscribers,
        'notifications': notifications,
        'sent_notifications_dataset': sent_notifications_dataset,
        'opened_notifications_dataset': opened_notifications_dataset,
        'labels_dataset': labels_dataset,
        'sent_notifications': sent_notifications,
        'remaining_notifications': remaining_notifications,
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def track(request, push_message_id=''):
    try:
        message = PushMessage.objects.get(id = push_message_id)
        message.opened_num += 1
        message.save()
    except PushMessage.DoesNotExist:
        message = None

    try:
        client = ClientProfile.objects.get(account_key = message.account_key)
    except ClientProfile.DoesNotExist:
        client = None

    if message and client:
        if message.custom:
            redirect_url = message.url_args
            if not message.url_args.startswith('http'):
                redirect_url = 'http://' + redirect_url
            return redirect(redirect_url)
        if len(client.url_format_string):
            return redirect(client.url_format_string + message.url_args + '&source=push_monkey')
        return redirect(client.website + "?p=" + message.url_args + '&source=push_monkey')
    raise Http404
