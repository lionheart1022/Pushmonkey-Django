from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import smart_str
from pushmonkey.models import PushMessage, Device, PayloadSafari, PushPackage, Batch, WebServiceDevice
from datetime import datetime, timedelta
from clients.models import ClientProfile
from djacobs_apns.apns import APNs, Frame
from django.conf import settings
from django.core.mail import send_mail
from plans.models import Plan
from plans.models import PlanVariant as plans
from emails.managers import EmailManager
from random import randint
import json
import logging
import os
import random
import time
import requests

logger = logging.getLogger('djacobs_apns.apns')

class Command(BaseCommand):

    def __init__(self):
        self.batch_raw = {}
        self.batch = Batch()

    def handle(self, *args, **options):
        push_message = None
        for message_id in args:
            try:
                push_message = PushMessage.objects.get(pk=int(message_id))
            except PushMessage.DoesNotExist:
                raise CommandError('PushMessage with ID "%s" does not exist' % message_id)

        push_message.title = push_message.title.strip(' \n\r')
        push_message.body = push_message.body.strip(' \n\r')
        push_message.save()

        device_num, feedback_responses = self.send_apns(push_message)
        device_num += self.send_google_notifications(push_message)
        device_num += self.send_mozilla_notifications(push_message)
        push_message.device_num = device_num
        push_message.save()

        self.send_email(push_message)
            
        message_lines = [
            "====== Push Monkey ====\n",
            "Send push with message ID " + str(push_message.id) + "\n",
            "title: " + push_message.title.encode('ascii', 'ignore') + "\n"
            "body: " + push_message.body.encode('ascii', 'ignore') + "\n"
            "and url args: " + push_message.url_args + "\n"
            "number of devices: " + str(push_message.device_num) + "\n"
            "Date: " + datetime.today().isoformat() + "\n"
            "Feedback Server: " + str(feedback_responses) + "\n"
            "=======================\n"
        ]
        logs_dir = '/var/lib/openshift/'+ settings.OPENSHIFT_ID +'/app-root/logs'
        f = open(os.path.join(logs_dir, 'push_sent_log.txt'), 'a')
        for message in message_lines:
            self.stdout.write(message)
            f.write(message.encode('utf8'))
        f.close()

    def send_apns(self, push_message):
        profile = ClientProfile.objects.get(account_key = push_message.account_key)
        if not profile.website_push_id:
            self.send_error_email('Website Push ID can\'t be empty')
        try:
            push_package = PushPackage.objects.get(identifier = push_message.account_key)
        except:
            push_package = None
        if push_package:
            cert_path = push_package.cert_pem.path
            key_path = push_package.key_pem.path
        else:
            cert_path = os.path.join(settings.STATIC_ROOT, profile.website_push_id, 'pushPackage', 'cert.pem')
            key_path = os.path.join(settings.STATIC_ROOT, profile.website_push_id, 'pushPackage', 'key.pem')
        apns = APNs(use_sandbox=False, cert_file=cert_path, key_file=key_path, enhanced = True)
        apns.gateway_server.register_response_listener(self.response_listener)
        devices = Device.objects.filter(account_key = profile.account_key)
        i = 0
        alert_dict = {"title": push_message.title, "body": push_message.body, "action": "View"}
        ### Single message version
        for device in devices:
            token = device.token
            identifier = random.getrandbits(32)
            self.batch_raw[identifier] = {"token": token, "resp_status": ""}
            if device.ported:
                payload = PayloadSafari(alert = alert_dict, url_args = [str(push_message.url_args)])
            else:
                payload = PayloadSafari(alert = alert_dict, url_args = [str(push_message.id)])
            try:
                apns.gateway_server.send_notification(token, payload, identifier = identifier)
                i += 1
            except Exception, e:
                apns = APNs(use_sandbox=False, cert_file=cert_path, key_file=key_path, enhanced = True)
                apns.gateway_server.send_notification(token, payload, identifier = identifier)
                i += 1
        self.batch.push_message = push_message
        self.batch.resp = json.dumps(self.batch_raw, sort_keys = True, indent = 4, separators = (',', ': '))
        self.batch.save()

        #contact feedback server
        feedback_responses = []
        apns = APNs(use_sandbox = False, cert_file = cert_path, key_file = key_path, enhanced = True)
        for (token_hex, fail_time) in apns.feedback_server.items():
            feedback_responses += [(token_hex, fail_time.isoformat())]
            #delete tokens that are returned by the feedback service
            try:
                devices_to_delete = Device.objects.filter(token = token_hex)
                for device in devices_to_delete:
                    device.delete()
            except Exception, e:
                print "================"
                print "Deletion failed: "
                print e
        apns.gateway_server.force_close()
        return i, feedback_responses

    def send_google_notifications(self, push_message):
        profile = ClientProfile.objects.get(account_key = push_message.account_key)
        devices = WebServiceDevice.objects.filter(account_key = profile.account_key, chrome = True)
        if len(devices) == 0:

            return
        subscription_ids = map(lambda d: d.subscription_id, devices)
        headers = {'Authorization': 'key=AIzaSyBE9L83MefDOq6PxeFU0m4LaerMvilLCsI',
        'Content-Type': 'application/json'}
        url = devices[0].endpoint
        data = {'registration_ids': subscription_ids}
        response = requests.post(url, headers = headers, data = json.dumps(data))
        if response.status_code != 200:

            print(response.text)
            return
        j = response.json()
        total = 0
        if j.has_key("results"):
            for i, result in enumerate(j["results"]):
                if result.has_key("message_id"):
                    total += 1
                elif result.has_key("error"):
                    device = WebServiceDevice.objects.filter(subscription_id = subscription_ids[i])
                    device.delete()
        return total

    def send_mozilla_notifications(self, push_message):
        profile = ClientProfile.objects.get(account_key = push_message.account_key)
        devices = WebServiceDevice.objects.filter(account_key = profile.account_key, mozilla = True)
        if len(devices) == 0:

            return
        subscription_ids = map(lambda d: d.subscription_id, devices)
        headers = {'TTL': '86400', 'Content-Type': 'application/json'}
        total = 0
        for s in subscription_ids:
            url = devices[0].endpoint + "/" + s
            response = requests.post(url, headers = headers)
            if response.status_code in [200, 201]:
                total += 1
        return total

    def response_listener(self, error_response):
        identifier = error_response['identifier']
        self.batch_raw[identifier]["resp_status"] += str(error_response['status'])
        self.batch.resp = json.dumps(self.batch_raw, sort_keys = True, indent = 4, separators = (',', ': '))
        self.batch.save()

    def send_email(self, push_message):
        # send an email to MANAGERS, for the record.
        emails = [person[1] for person in settings.MANAGERS]
        subject = 'Push sent: ' + push_message.title + ' to ' + str(push_message.device_num) + ' devices'
        message = 'Message: ' + push_message.body
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)

        # send stats email to client
        profile = ClientProfile.objects.get(account_key = push_message.account_key)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [profile.user.email], fail_silently = False) 

        # check if allocated number of notifications has been exceeded
        remaining_days = 0
        try:
            plan = Plan.objects.exclude(type = plans.NONE).exclude(status = 'expired').filter(user = profile.user, status = 'active').latest('created_at')
            remaining_days = (plan.end_at - datetime.now()).days
        except Plan.DoesNotExist:
            plan = None
        if plan:
            next_plan_name = "Sweet Spot Plan" 
            if plan.type == 2:
                next_plan_name = "Pro"
            subscribers = Device.objects.filter(account_key = profile.account_key).count()
            sent_notifications = PushMessage.objects.sent_notifications_count(account_key = push_message.account_key)
            if sent_notifications >= plan.number_of_notifications:
                em = EmailManager()
                em.send_notif_number_exceeded(to_email = profile.user.email,
                                              first_name = profile.user.first_name,
                                              remaining_days = remaining_days,
                                              subscribers = subscribers,
                                              next_plan_name = next_plan_name)

    def send_error_email(self, message):
        # send an email to MANAGERS, for the record.
        emails = [person[1] for person in settings.MANAGERS]
        subject = 'Something went wrong'
        send_mail(subject, message, settings.EMAIL_HOST_USER, emails, fail_silently=False)

