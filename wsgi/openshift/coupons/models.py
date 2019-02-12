from django.db import models
from plans.models import Plan, PlanVariant
from django.contrib.auth.models import User
import string, random
from datetime import datetime

TYPE_CHOICES = (
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
)

PLAN_CHOICES = (
    (PlanVariant.STARTER, 'Starter'),
    (PlanVariant.SWEET_SPOT, 'Sweet Spot'),
    (PlanVariant.PRO, 'Pro'),
)

COUPON_TYPE_CHOICES = (
    ('discount', 'Discount'),
    ('fixed_price', 'Fixed Price'),
)

class Coupon(models.Model):
    string = models.CharField(max_length = 20, help_text = "Don't enter any values in here. This field is automatically generated.", default = '', blank = True)
    time_unit = models.CharField(choices = TYPE_CHOICES, max_length = 40, default = TYPE_CHOICES[0][0])
    time_unit_count = models.IntegerField(help_text = "Number of months/years that this coupon enables", default = 0)
    plan = models.IntegerField(choices = PLAN_CHOICES, max_length = 40, default = PLAN_CHOICES[0][0])
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)
    start_at = models.DateTimeField(default = datetime.now, blank = True, null = True)
    end_at = models.DateTimeField(default = datetime.now)
    redeemed = models.BooleanField(default = False)
    user = models.ForeignKey(User, blank = True, null = True)

    def __unicode__(self):
        return self.string + ' - '+ self.get_time_unit_display() + ' ' + str(self.time_unit_count) + ' - ' + self.get_plan_display()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.string = ''.join(random.sample(string.uppercase + '1234567890', 17)) 
        super(Coupon, self).save(*args, **kwargs)

    def admin_plan(self):
        return self.get_plan_display()
    admin_plan.short_description = 'Plan'

class DiscountCoupon(models.Model):
    string = models.CharField(max_length = 20, help_text = "Don't enter any values in here. This field is automatically generated.", default = '', blank = True)
    valid = models.BooleanField(default = False)
    single_use = models.BooleanField(help_text = "True if the coupon can be used a single time.", default = False)
    created_at = models.DateTimeField(default = datetime.now)
    redeemed_at = models.DateTimeField(default = datetime.now)
    user = models.ForeignKey(User, blank = True, null = True)
    plan_type = models.IntegerField(choices = PLAN_CHOICES, max_length = 40, default = PLAN_CHOICES[0][0])
    time_unit = models.CharField(choices = TYPE_CHOICES, max_length = 40, default = TYPE_CHOICES[0][0])
    type = models.CharField(verbose_name = "Coupon Type", help_text = "Discount means a percentage. E.g. 20 for 20% (don't type the % sign). Fixed price means that a fixed price will be used for the selected plan.", choices = COUPON_TYPE_CHOICES, max_length = 40, default = COUPON_TYPE_CHOICES[0][0])
    value = models.IntegerField(help_text = "Depending on the selected Plan Type", default = 0)

    def __unicode__(self):
        return str(self.string) + ' - ' + str(self.user)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.string = ''.join(random.sample(string.uppercase + '1234567890', 17)) 
        super(DiscountCoupon, self).save(*args, **kwargs)

    def should_show_monthly(self):
        if self.time_unit == TYPE_CHOICES[0][0]:
            return True
        return False

    def should_show_yearly(self):
        if self.time_unit == TYPE_CHOICES[1][0]:
            return True
        return False
