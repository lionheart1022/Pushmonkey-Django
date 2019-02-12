from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from models import Affiliate, AffiliateLink, RegisteredUser, AffiliatePayment, Payout
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.http import Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from managers import AffiliateEmailManager

def join(request):
    response = redirect('affiliates_center')
    return render_to_response('affiliates/join.html', 
                              {
                              },
                             RequestContext(request))

def center(request):
    if not request.user.is_authenticated():
        return redirect('register')

    should_show_modal = True
    referer_url = request.META.get('HTTP_REFERER', '')
    if referer_url.find(settings.LOGIN_URL) >= 0:
        should_show_modal = False
    if request.GET.get('use_current', None):
        should_show_modal = False
    af_link = None
    should_send_welcome_email = False
    af = None
    if not should_show_modal:
        af, created = Affiliate.objects.get_or_create(user = request.user)
        if created:
            af_link = AffiliateLink.objects.create(affiliate = af)
            af_link.save()
            should_send_welcome_email = True
        else:
            try:
                af_link, af_link_created = AffiliateLink.objects.get_or_create(affiliate = af)
                if af_link_created:
                    should_send_welcome_email = True
            except AffiliateLink.MultipleObjectsReturned:
                af_link = AffiliateLink.objects.filter(affiliate = af)[0]

    if should_send_welcome_email:
        em = AffiliateEmailManager()
        em.send_welcome_email(request.user.email, request.user.first_name, af_link.token)

    affiliate_payments = []
    if af:
        registered_users = RegisteredUser.objects.filter(affiliate = af)
        for registered_user in registered_users:
            affiliate_payments += AffiliatePayment.objects.filter(registered_user = registered_user)

    total_received = 0
    total_to_receive = 0
    for payment in affiliate_payments:
        if payment.payed_to_user:
            total_received += payment.sum_value()
        else:
            total_to_receive += payment.sum_value()

    disable_payout_button = False
    if af:
        if Payout.objects.filter(affiliate = af, honored = False):
                disable_payout_button = True

    insuficient_payout_sum = False
    if total_to_receive < 20:
        insuficient_payout_sum = True
        disable_payout_button = True

    banners = [
        {'id': 'recommended', 
         'name': 'Recommended',
         'images': [
             {'size': '300x250', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-250-v8.png', 
              'name': 'banner-300-250-v8.png'},
             {'size': '300x250', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-250-v9.png', 
              'name': 'banner-300-250-v9.png'},
             {'size': '300x250', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-250-v5.png', 
              'name': 'banner-300-250-v5.png'},
             {'size': '300x250', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-250-v6.png', 
              'name': 'banner-300-250-v6.png'},
             {'size': '300x250', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-250-v7.png', 
              'name': 'banner-300-250-v7.png'},
             {'size': '300x250', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-250-v11.png', 
              'name': 'banner-300-250-v11.png'},
         ]
        },
        {'id': 'wide', 
         'name': 'Wide',
         'images': [
             {'size': '728x90', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-728-90-v1.png', 
              'name': 'banner-728-90-v1.png'},
             {'size': '728x90', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-728-90-v2.png', 
              'name': 'banner-728-90-v2.png'},
         ]
        },
        {'id': 'tall', 
         'name': 'Tall',
         'images': [
             {'size': '160x600', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-160-600-v1.png', 
              'name': 'banner-160-600-v1.png'},
             {'size': '160x600', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-160-600-v2.png', 
              'name': 'banner-160-600-v2.png'},
             {'size': '300x600', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-600-v1.png', 
              'name': 'banner-300-600-v1.png'},
             {'size': '300x600', 
              'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-300-600-v2.png', 
              'name': 'banner-300-600-v2.png'},
         ]
        },
    {'id': 'small', 
     'name': 'Small/Mobile',
     'images': [
         {'size': '320x50', 
          'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-320-50-v1.png', 
          'name': 'banner-320-50-v1.png'},
         {'size': '320x50', 
          'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-320-50-v2.png', 
          'name': 'banner-320-50-v2.png'},
         {'size': '125x125', 
          'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-125-125-v1.png', 
          'name': 'banner-125-125-v1.png'},
         {'size': '125x125', 
          'src': 'https://dl.dropboxusercontent.com/u/1618599/cdn/push-monkey/banner-125-125-v2.png', 
          'name': 'banner-125-125-v2.png'},
     ]
    },
    ]

    return render_to_response('affiliates/center.html', 
                              {'af_link': af_link,
                               'should_show_modal': should_show_modal,
                               'affiliate_payments': affiliate_payments,
                               'total_received': total_received,
                               'total_to_receive': total_to_receive,
                               'disable_payout_button': disable_payout_button,
                               'insuficient_payout_sum': insuficient_payout_sum,
                               'banners': banners,
                              },
                             RequestContext(request))

@login_required
def request_payout(request):
    try:
        af = Affiliate.objects.get(user = request.user)
        payout = Payout(affiliate = af)
        payout.save()
        em = AffiliateEmailManager()
        em.send_payout_request_email(request.user.email)
    except Affiliate.DoesNotExist:
        pass
    response = redirect('affiliates_center')
    response['Location'] += '?use_current=1'
    return response


def track(request, token = ''):
    affiliate_link = None
    try:
        affiliate_link = AffiliateLink.objects.get(token = token)
        affiliate_link.opened_counter += 1
        affiliate_link.save()
    except:
        pass
    if affiliate_link:
        response = HttpResponseRedirect(reverse('register') + '?affiliate=1') 
        max_age = 24 * 60 * 60 * 7 #7 days
        response.set_cookie('push_monkey_affiliate_token', token, max_age = max_age, httponly=True)
        return response
    raise Http404
