from clients.models import ClientProfile
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from plans.managers import PlansEmailManager 
from plans.models import Plan
from plans.models import PlanVariant 
from pushmonkey.models import Device

class Command(BaseCommand):

    def handle(self, *args, **options):
        plans = Plan.objects.filter(status = 'active')
        for plan in plans:
            if plan.end_at < datetime.now():
                plan.status = 'expired'
                plan.save()
            delta = plan.end_at - datetime.now()
            if delta.days == 10 and plan.type == PlanVariant.TRIAL :
                manager = PlansEmailManager()
                profile = ClientProfile.objects.get(user = plan.user)
                devices = Device.objects.filter(account_key = profile.account_key)
                manager.send_trial_pre_expiration(to_email = plan.user.email, first_name = plan.user.first_name, subscribers = devices.count())

