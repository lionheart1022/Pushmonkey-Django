from clients.models import ClientProfile
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from pushmonkey.managers import PushMonkeyEmailManager
from pushmonkey.models import PushMessage, Device, WebServiceDevice

class Command(BaseCommand):

  def handle(self, *args, **options):

    profiles = ClientProfile.objects.filter(
      confirmed = True, 
      status = "active", 
      registration_step = 4,
      account_key__isnull = False)
    email_manager = PushMonkeyEmailManager()
    for profile in profiles:

      account_key = profile.account_key
      subscribers = Device.objects.filter(account_key = account_key).count()
      subscribers += WebServiceDevice.objects.filter(account_key = account_key).count()
      last_week = datetime.now() - timedelta(days = 7)
      new_subscribers = Device.objects.filter(account_key = account_key, 
        created_at__gte = last_week).count()
      new_subscribers += WebServiceDevice.objects.filter(account_key = account_key, 
        created_at__gte = last_week).count()
      present = subscribers
      past = subscribers - new_subscribers
      if past > 0:
        growth = (present - past)/past
      else:
        growth = 0
      notifications = PushMessage.objects.filter(account_key = account_key, 
        created_at__gte = last_week).count()
      email_manager.send_weekly_report_email(profile.user.email, 
        profile.user.first_name, 
        subscribers,
        new_subscribers,
        growth,
        notifications)