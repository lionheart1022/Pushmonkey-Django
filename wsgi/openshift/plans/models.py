from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core import exceptions
from django.core.mail import send_mail
from django.db import models
from managers import PlansEmailManager
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.ipn.signals import payment_was_successful
import json, math
import helpers

class PlanVariant:
    NONE = 0
    STARTER = 1
    SWEET_SPOT = 2
    PRO = 3
    CUSTOM = 4
    TRIAL = 5
    FIXED = 6

    def starter_monthly(self):
        return str(self.STARTER)+"-M"

    def starter_yearly(self):
        return str(self.STARTER)+"-Y"

    def sweet_spot_monthly(self):
        return str(self.SWEET_SPOT)+"-M"

    def sweet_spot_yearly(self):
        return str(self.SWEET_SPOT)+"-Y"

    def pro_monthly(self):
        return str(self.PRO)+"-M"

    def pro_year(self):
        return str(self.PRO)+"-Y"

PLAN_CHOICES = (
    (PlanVariant.NONE, 'No selected'),
    (PlanVariant.STARTER, 'Starter'),
    (PlanVariant.SWEET_SPOT, 'Sweet Spot'),
    (PlanVariant.PRO, 'Pro'),
    (PlanVariant.CUSTOM, 'Custom'),
    (PlanVariant.TRIAL, 'Trial'),
    (PlanVariant.FIXED, 'Fixed Price'),
)

STATUS_CHOICES = (
    ('pending', 'Pending Payment'),
    ('active', 'Active'),
    ('expired', 'Expired'),
)

#TODO: move this inside class
def is_black_friday():
    now = datetime.now()
    if now.year == 2014 and now.month == 11 and now.day == 28 and now.hour >= 2:
        return True
    return False

def is_cool_update_offer():
    return False

def calculate_starter_monthly():
    if is_cool_update_offer():
        return 3
    return 11.99

def calculate_starter_yearly():
    if is_cool_update_offer():
        return 29 
    return 9.99 * 12

def calculate_sweet_spot_monthly():
    if is_black_friday():
        return 1
    return 24.99

def calculate_sweet_spot_yearly():
    if is_black_friday():
        return 12
    return 19.99 * 12

#TODO: move this outside, because a server restart is
# required to update the values
class Prices(object):

    STARTER_MONTHLY = 11.99
    STARTER_YEARLY = 9.99 * 12
    SWEET_SPOT_MONTHLY = calculate_sweet_spot_monthly()
    SWEET_SPOT_YEARLY = calculate_sweet_spot_yearly()
    PRO_MONTHLY = 34.99
    PRO_YEARLY = 29.99 * 12
    
    @classmethod
    def starter_monthly_paid_yearly(self):
        return self.STARTER_YEARLY/12.0

    @classmethod
    def sweet_spot_monthly_paid_yearly(self):
        return self.SWEET_SPOT_YEARLY/12.0

    @classmethod
    def pro_monthly_paid_yearly(self):
        return self.PRO_YEARLY/12.0

class PlanManager(models.Manager):

    def get_current_plan_for_user(self, user):
        """
        Returns the current active plan for a User (or None if no matching plan found) and
        a flag to mark if all of the User's plans are expired.
        """
        plan = None
        has_only_expired_plans = False
        try:
            plan = Plan.objects.exclude(status = 'expired').exclude(type = PlanVariant.NONE).get(user = user, status = 'active')
        except exceptions.MultipleObjectsReturned:
            plan = Plan.objects.exclude(status = 'expired').exclude(type = PlanVariant.NONE).filter(user = user, status = 'active', start_at__lte = datetime.now()).latest('end_at')
        except Plan.DoesNotExist:
            #check for expired plans
            plan_count = Plan.objects.filter(user = user, status = 'expired').exclude(type = PlanVariant.NONE).count()
            if plan_count:
                has_only_expired_plans = True
        return plan, has_only_expired_plans

    def already_had_trial(self, user):
        if Plan.objects.filter(user = user, type = PlanVariant.TRIAL).count() >= 1:
            return True
        else:
            return False

    def create_fixed_plan(self, user):
        plan = Plan(user = user, 
                    type = PlanVariant.FIXED,
                    end_at = datetime.now() + timedelta(days=365 * 3),
                    status = 'active',
                    payed = True)
        plan.save()
        return plan


class Plan(models.Model):
    user = models.ForeignKey(User)
    type = models.IntegerField(choices=PLAN_CHOICES)
    number_of_notifications = models.IntegerField(default=10000)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)
    start_at = models.DateTimeField(default=datetime.now)
    end_at = models.DateTimeField(default=datetime.now)
    payed = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0], max_length=50)
    txn_id = models.CharField("Transaction ID", max_length=19, blank=True)

    objects = PlanManager()

    def __unicode__(self):
        return self.user.username + ' - '+ self.get_type_display() + ' - ' + self.get_status_display()

    def is_trial(self):
        return self.type == PlanVariant.TRIAL

    def is_pending(self):
        return self.status == 'pending'

    def is_expired(self):
        return self.status == 'expired'

    def is_pro(self):
        return self.type == PlanVariant.PRO

    def notify_user_of_payment(self):
        email_manager = PlansEmailManager()
        email_manager.send_plan_activation(to_email = self.user.email, first_name = self.user.first_name, plan_name = self.get_type_display())
        #send email to ADMINS
        email_manager.send_admin_new_plan(self.user.email, self.user.first_name, self)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.type == PlanVariant.TRIAL:
                self.number_of_notifications = 2000000
            elif self.type == PlanVariant.STARTER:
                self.number_of_notifications = 10000
            elif self.type == PlanVariant.SWEET_SPOT:
                self.number_of_notifications = 500000
            elif self.type == PlanVariant.PRO:
                self.number_of_notifications = 1500000
            elif self.type == PlanVariant.FIXED:
                self.number_of_notifications = 5000
        super(Plan, self).save(*args, **kwargs)

    def original_transaction(self):
        """
        Returns the PayPalIPN object that has the txn_id of this plan
        """
        if not len(self.txn_id):
            return None
        try:
            ipn = PayPalIPN.objects.get(txn_id = self.txn_id)
        except PayPalIPN.DoesNotExist:
            return None
        return ipn
    
    def plan_length(self):
        if (self.end_at - self.start_at).days > 31:
            return 'yearly'
        else:
            return 'monthly'

    def price(self):
        if self.plan_length() == 'yearly':
            if self.type == 1:
                return Prices.STARTER_YEARLY
            elif self.type == 2:
                return Prices.SWEET_SPOT_YEARLY
            elif self.type == 3:
                return Prices.PRO_YEARLY
        elif self.plan_length() == 'monthly':
            if self.type == 1:
                return Prices.STARTER_MONTHLY
            elif self.type == 2:
                return Prices.SWEET_SPOT_MONTHLY
            elif self.type == 3:
                return Prices.PRO_MONTHLY
        return 0.0

def mark_payment(sender, **kwargs):
    ipn_obj = sender

    if ipn_obj.payment_status == "Completed":
        info = json.loads(ipn_obj.custom) 
        user_id = info.get('user_id')
        plan_type = info.get('plan_type')
        time_units = info.get('time_units')
        user = User.objects.get(id = user_id)
        end_at = datetime.now() + timedelta(days = 365)
        if time_units == 'M':
            end_at = datetime.now() + timedelta(days = 30)
        if Plan.objects.filter(txn_id = ipn_obj.txn_id).count() == 0:
            plan = Plan(user = user, 
                        type = plan_type,
                        end_at = end_at,
                        payed = True,
                        status = 'active',
                        txn_id = ipn_obj.txn_id)
            plan.save()
            plan.notify_user_of_payment()
            profile = helpers.get_profile_for_user_id(user_id)
            if profile:
                package = helpers.create_push_package_for_profile(profile)
        else: # there already is a plan for this transaction. Ignore.
            pass
    else:
        #send email to MANAGERS
        emails = [person[1] for person in settings.MANAGERS]
        subject = 'A payment failed: payment id ' + str(ipn_obj.id)
        message = 'Check it out in the admin'
        send_mail(subject, message, settings.EMAIL_HOST_USER, emails, fail_silently=False)
payment_was_successful.connect(mark_payment)
