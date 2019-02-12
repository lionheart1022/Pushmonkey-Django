from models import Coupon
from forms import RedeemForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from plans.models import Plan, PlanVariant
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

@login_required
def redeem(request):
    redeemed = False
    plan = None
    if request.method == "POST":
        form = RedeemForm(data=request.POST)
        if form.is_valid():
            #mark coupon as redeemed
            code = form.cleaned_data['code']
            coupon = Coupon.objects.get(string = code)
            coupon.redeemed = True
            coupon.user = request.user
            coupon.save()
            redeemed = True
            #create a new plan for this coupon
            end_at = datetime.now() + timedelta(days = 365 * coupon.time_unit_count) 
            if coupon.time_unit == 'monthly':
                end_at = datetime.now() + timedelta(days = 30 * coupon.time_unit_count)
            plan = Plan(user = request.user, 
                        type = coupon.plan,
                        end_at = end_at,
                        status = 'active',
                        payed = False,
                        txn_id = 'Coupon')
            plan.save()
            redeemed = True
    else:
        form = RedeemForm()

    return render_to_response('coupons/redeem.html', 
                              {'form': form,
                               'redeemed': redeemed,
                               'plan': plan,
                               'plans': PlanVariant,
                              },
                             RequestContext(request))
