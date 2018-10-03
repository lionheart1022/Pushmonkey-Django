from clients.models import ClientProfile, ProfileImage
from coupons.models import DiscountCoupon
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from forms import DiscountCouponForm
from managers import PlansEmailManager
from models import PlanVariant as plans
from models import Plan
from models import Prices as prices
from paypal.standard.forms import PayPalPaymentsForm
from pushmonkey.managers import PushPackageManager
from pushmonkey.models import PushPackage
import random
import json

@login_required
def payment_overview(request, type = 'monthly', selected_plan = 3, coupon_id = None):
    monthly_selected = (type == 'monthly')
    yearly_selected = (type == 'yearly')
    selected_plan = int(selected_plan)
    price_monthly = prices.SWEET_SPOT_MONTHLY
    price_full_yearly = 180
    price_yearly = prices.sweet_spot_monthly_paid_yearly()
    full_price_yearly = prices.SWEET_SPOT_YEARLY
    plan_name = "Sweet Spot Plan"
    if selected_plan == plans.STARTER:
        price_monthly = prices.STARTER_MONTHLY
        price_full_yearly = 108
        price_yearly = prices.starter_monthly_paid_yearly()
        full_price_yearly = prices.STARTER_YEARLY
        plan_name = "Starter Plan"
    elif selected_plan == plans.PRO:
        price_monthly = prices.PRO_MONTHLY 
        price_full_yearly = 348
        price_yearly = prices.pro_monthly_paid_yearly()
        full_price_yearly = prices.PRO_YEARLY
        plan_name = "Pro Plan"

    price = price_monthly
    plan_name_monthly = "Push Monkey - " + plan_name + " - Monthly Subscription"
    plan_name_yearly = "Push Monkey - " + plan_name + " - Yearly Subscription"
    selected_plan_name = plan_name_monthly
    if yearly_selected:
        price = full_price_yearly
        selected_plan_name = plan_name_yearly

    time_units_count = 1
    if yearly_selected:
        time_units_count = 1

    time_units = "M"
    if yearly_selected:
        time_units = "Y"

    coupon_form = DiscountCouponForm(initial = {'selected_plan': selected_plan, 'time_unit': type})
    coupon = None
    try:
        coupon = DiscountCoupon.objects.get(id = coupon_id)
        if coupon.should_show_yearly():
            yearly_selected = True
            if coupon.type == 'discount':
                price_yearly = price_yearly * coupon.value / 100.0
            else:
                price_yearly = coupon.value
            price = price_yearly
            time_units = "Y"
        elif coupon.should_show_monthly():
            monthly_selected = True
            if coupon.type == 'discount':
                price_monthly = price_monthly * coupon.value / 100.0
            else:
                price_monthly = coupon.value
            price = price_monthly
            time_units = "M"
    except:
        pass

    site = Site.objects.get_current()
    paypal_dict = {
        "cmd": "_xclick-subscriptions",
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": price,
        "item_name": selected_plan_name,
        "notify_url": "https://" + site.domain + reverse('paypal-ipn'),
        "return_url": "https://" + site.domain + reverse('payment_processing', args=[selected_plan]),
        "cancel_return": "https://" + site.domain + reverse('payment_cancelled'),
        "a3": price,
        "p3": time_units_count,
        "t3": time_units,
        "src": "1",
        "no_note": "1",
        "custom": json.dumps({'user_id': request.user.id, 'plan_type': selected_plan, 'time_units': time_units})
    }
    form = PayPalPaymentsForm(button_type = "subscribe", initial=paypal_dict)

    return render_to_response('plans/payment_overview.html', 
                              {'monthly_selected': monthly_selected,
                               'yearly_selected': yearly_selected,
                               'selected_plan': selected_plan,
                               'price_monthly': price_monthly,
                               'price_full_yearly': price_full_yearly,
                               'price_yearly': price_yearly,
                               'full_price_yearly': full_price_yearly,
                               'plan_type': type,
                               'plans': plans,
                               'form': form,
                               'plan_name_yearly': plan_name_yearly,
                               'plan_name_monthly': plan_name_monthly,
                               'plan_name': plan_name,
                               'coupon_form': coupon_form,
                               'coupon': coupon,
                              }, 
                              RequestContext(request))


@login_required
def payment_apply_coupon(request):
    if request.method == 'POST':
        form = DiscountCouponForm(data = request.POST)
        if form.is_valid():
            coupon_string = form.cleaned_data.get('coupon_string', None)
            selected_plan = form.cleaned_data.get('selected_plan', None)
            time_unit = form.cleaned_data.get('time_unit', None)
            error_redirect = redirect(reverse('payment_overview', args = [time_unit, selected_plan])) 
            if not coupon_string:
                messages.error(request, 'The coupon code is invalid. Error #1')
                return error_redirect 
            coupon = None
            try:
                coupon = DiscountCoupon.objects.get(string = coupon_string)
            except:
                messages.error(request, 'The coupon code is invalid. Error #2')
                return error_redirect 
            if not coupon.valid:
                messages.error(request, 'The coupon code is invalid. Error #3')
                return error_redirect 
            if not str(coupon.plan_type) == str(selected_plan):
                messages.error(request, 'The coupon code is not valid for this plan type. Error #4')
                return error_redirect 
            return redirect(reverse('payment_overview_coupon', args = [time_unit, selected_plan, coupon.id]))
        else:
            print form.errors

    raise Http404

@login_required
@csrf_exempt
def payment_cancelled(request):
    return render_to_response('plans/payment_cancelled.html', 
                             {},
                             RequestContext(request))

@login_required
@csrf_exempt
def payment_processing(request, selected_plan = None):
    if selected_plan:
        selected_plan = int(selected_plan)
    try:
        profile = ClientProfile.objects.get(user = request.user)
    except:
        profile = None
    if profile and not profile.has_push_package():
        if profile.registration_step == 3:
            profile.registration_step = 4
            profile.save()
        package_manager = PushPackageManager()
        package = package_manager.get_push_package(profile)
        if package:
            profile_image = ProfileImage.objects.get(profile = profile)
            package.generate_zip(profile.website_name, 
                                 profile.website,
                                 profile_image.image128_2x.path,
                                 profile_image.image128.path,
                                 profile_image.image32_2x.path,
                                 profile_image.image32.path,
                                 profile_image.image16_2x.path,
                                 profile_image.image16.path,
                                )
            profile.status = 'active'
            profile.account_key = package.identifier
            profile.website_push_id = package.website_push_id
            profile.save()
            package.used = True
            package.save()
        else:
            profile.status = 'pending'
            profile.save()
        url = profile.return_url
        if len(url):
            if package:
                if url.find('?') > 0:
                    url += "&push_monkey_account_key=" + profile.account_key + "&push_monkey_registered=1"
                else:
                    url += "?push_monkey_account_key=" + profile.account_key + "&push_monkey_registered=1"
            else:
                url += "&push_monkey_package_pending=1&push_monkey_registered=1"
            return HttpResponseRedirect(url)

    return render_to_response('plans/payment_processing.html', 
                              {
                                  'selected_plan': selected_plan, 
                                  'plans': plans
                              },
                              RequestContext(request))

@login_required
def trial_thank_you(request):
    plan = Plan(user = request.user, 
                type = plans.TRIAL,
                end_at = datetime.now() + timedelta(days=30),
                status = 'active',
                payed = False)
    plan.save()
    #send email to ADMINS
    email_manager = PlansEmailManager()
    email_manager.send_admin_new_plan(request.user.email, request.user.first_name, plan)
    return render_to_response('plans/trial_thank_you.html',
                              {},
                              RequestContext(request))
