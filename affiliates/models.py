from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import string, random
from plans.models import Plan
from django.dispatch import receiver
from django.db.models.signals import post_save

class Affiliate(models.Model):
    user = models.ForeignKey(User)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return str(self.user)

class AffiliateLink(models.Model):
    affiliate = models.ForeignKey(Affiliate)
    token = models.CharField(max_length = 300, default = '')
    opened_counter = models.IntegerField(default = 0)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return 'Affiliate User: ' + str(self.affiliate) + ' - ' + self.token

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = ''.join(random.sample(string.uppercase + '1234567890', 6)) 
        super(AffiliateLink, self).save(*args, **kwargs)

class RegisteredUser(models.Model):
    affiliate = models.ForeignKey(Affiliate)
    registered_user = models.ForeignKey(User)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return str(self.registered_user) + ' invited by ' + str(self.affiliate) 

class AffiliatePayment(models.Model):
    registered_user = models.ForeignKey(RegisteredUser)
    commision = models.FloatField(default = 0, help_text = "% that we give to the referer")
    original_payed_sum = models.DecimalField(max_digits=64, decimal_places=2, default=0, blank=True, null=True)
    payed_to_user = models.BooleanField(default = False)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)
    plan = models.ForeignKey(Plan, null = True, blank = True)

    def __unicode__(self):
        return str(self.registered_user.affiliate) + ' invited ' + str(self.registered_user.registered_user) + '; plan: ' + str(self.plan.get_type_display()) 

    def sum_value(self):
        return self.plan.price() * (self.commision/100.0)

@receiver(post_save, sender=Plan)
def mark_affiliated_payment(sender, **kwargs):
    plan = kwargs.get('instance')
    if not plan.payed:
        return
    activation_interval = (plan.end_at - plan.start_at)
    monthly = True
    if activation_interval.days > 300:
        monthly = False
    try:
        registered_user = RegisteredUser.objects.get(registered_user = plan.user)
    except RegisteredUser.DoesNotExist:
        return
    affiliate_payment, created = AffiliatePayment.objects.get_or_create(plan = plan, registered_user = registered_user)
    affiliate_payment.commision = 25.0
    if monthly:
        affiliate_payment.commision = 40.0
    if plan.original_transaction():
        affiliate_payment.original_payed_sum = plan.original_transaction().mc_gross
    affiliate_payment.save()

class Payout(models.Model):
    affiliate = models.ForeignKey(Affiliate)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)
    honored = models.BooleanField(default = False)
    comment = models.CharField(max_length = 300, default = '')

    def __unicode__(self):
        return str(self.affiliate)
