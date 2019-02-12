from affiliates.models import RegisteredUser, AffiliateLink
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from forms import UserForm, ClientProfileForm, ResendConfirmForm, ProfileImageForm, CustomiseForm, LoginForm, WebsiteForm
from managers import ClientsEmailManager
from models import ClientProfile, ProfileConfirmation, ProfileImage
from plans.managers import PlansEmailManager
from plans.models import PlanVariant as plans
from plans.models import PlanVariant, Plan
from plans.models import Prices as prices
from pushmonkey.managers import PushPackageManager
from pushmonkey.models import PushMessage, Device, PushPackage
from website_clusters.helpers import website_from_profile, clean_website_url
from website_clusters.models import WebsiteCluster, Website, WebsiteIcon
import hashlib
import json
import os
import random
import shutil

@never_cache
def register(request, preselected_plan = None):
    registering = request.GET.get('registering', False)
    if request.method == 'POST':
        email_manager = ClientsEmailManager()
        user_form = UserForm(data=request.POST)
        profile_form = ClientProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            #UserForm
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.username = user.email[0:28] #Because emails can be much longer than 30 chars, the limit for a username
            user.save()

            #ClientProfileForm
            profile = profile_form.save(commit=False)
            profile.user = user
            if preselected_plan:
                profile.preselected_plan = preselected_plan 
            profile.save()

            #send email to ADMINS
            email_manager.send_admin_new_client(user.email)

            #create profile confirmation
            confirmation_key = hashlib.sha224(str(profile.id)).hexdigest()
            confirmation = ProfileConfirmation(profile = profile, confirmation_key = confirmation_key)
            confirmation.save()

            #affiliate
            affiliate_token = request.COOKIES.get('push_monkey_affiliate_token', None)
            if affiliate_token:
                try:
                    affiliate_link = AffiliateLink.objects.get(token = affiliate_token)
                except AffiliateLink.DoesNotExist:
                    affiliate_link = None
                if affiliate_link:
                    registered_user = RegisteredUser(affiliate = affiliate_link.affiliate, registered_user = user)
                    registered_user.save()

            #send confirmation email
            email_manager.send_confirmation_link_email(to_email = user.email, 
                                                       first_name = user.first_name, 
                                                       confirmation_key = confirmation_key)
            return HttpResponseRedirect(reverse('customise') + "?profile_id=" + str(profile.id))
    else:
        website = request.GET.get('websiteURL', '')
        website_name = request.GET.get('websiteName', '')
        return_url = request.GET.get('returnURL', '')
        email = request.GET.get('email', '')
        first_name = request.GET.get('first_name', '')
        from_envato = request.GET.get('envato', False)
        user_form = UserForm(initial = {
            'email': email,
            'first_name': first_name,
        })
        profile_form = ClientProfileForm(initial = {
            'website': website,
            'website_name': website_name,
            'return_url': return_url,
            'from_envato': from_envato,
        })
    
    return render_to_response('clients/register.html', 
                              {'user_form': user_form, 
                               'profile_form': profile_form,
                               'registering': registering,
                              }, 
                              RequestContext(request))

def register_thank_you(request, profile_id = None):
    try:
        profile = ClientProfile.objects.get(id = profile_id)
        if profile.registration_step != 3:

            raise Http404("Wrong user.")
        profile.registration_step = 4
        profile.save()
    except:
        raise Http404("Reached register_thank_you with no ClientProfile. profile_id=" + str(profile_id))
    if profile.has_push_package():
        return redirect('dashboard')
    if profile.status == 'active':
        return redirect('dashboard')
    #push package
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
    #plan
    if profile.from_envato:
        plan = Plan.objects.create_fixed_plan(profile.user)
    else:
        plan = Plan(user = profile.user, 
                    type = plans.TRIAL,
                    end_at = datetime.now() + timedelta(days=30),
                    status = 'active',
                    payed = False)
    plan.save()
    #send email to ADMINS
    email_manager = PlansEmailManager()
    email_manager.send_admin_new_plan(profile.user.email, profile.user.first_name, plan)
    url = profile.return_url
    if len(url):
        #redirect back to WP
        if package:
            if url.find('?') > 0:
                url += "&push_monkey_account_key=" + profile.account_key + "&push_monkey_registered=1"
            else:
                url += "?push_monkey_account_key=" + profile.account_key + "&push_monkey_registered=1"
        else:
            url += "&push_monkey_package_pending=1&push_monkey_registered=1"
        return HttpResponseRedirect(url)
    
    return render_to_response('clients/register-thank-you.html', 
                              {},
                              RequestContext(request))

@never_cache
def register_confirm(request, confirmation_key=""):
    invalid_key = False
    confirmed = False
    form = AuthenticationForm(request)
    if not len(confirmation_key):
        invalid_key = True
    try:
        profile_confirmation = ProfileConfirmation.objects.get(confirmation_key=confirmation_key)
        profile_confirmation.confirmed_at = datetime.now()
        profile_confirmation.save()
        profile_confirmation.profile.confirmed = True
        profile_confirmation.profile.save()
        confirmed = True

        email_manager = ClientsEmailManager()
        user = profile_confirmation.profile.user
        email_manager.send_welcome_email(to_email = user.email, first_name = user.first_name)
    except ProfileConfirmation.DoesNotExist:
        invalid_key = True
    return render_to_response('clients/login.html', 
                              {'invalid_key': invalid_key, 
                               'confirmed': confirmed, 
                               'form': form, 
                               'action_url': reverse('login')}, 
                              RequestContext(request))

def resend_confirm(request):
    MAX_CONFIRMATIONS = 5
    error_message = None
    resent = False
    if request.method == "POST":
        form = ResendConfirmForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                confirmation = ProfileConfirmation.objects.get(profile__user__email = email)
                if confirmation.number_of_resends >= MAX_CONFIRMATIONS:
                    error_message = "You already sent too many confirmation emails. Something seems wrong. Please contact us at hello@getpushmonkey.com"
                else:
                    confirmation.number_of_resends += 1
                    confirmation.save()
                    confirmation_key = confirmation.confirmation_key
                    user = confirmation.profile.user
                    confirmation_emails = [user.email]
                    email_manager = ClientsEmailManager()
                    email_manager.send_confirmation_link_email(to_email = user.email, 
                                                               first_name = user.first_name, 
                                                               confirmation_key = confirmation_key)
                    resent = True
            except ProfileConfirmation.DoesNotExist:
                error_message = "There seems to be no account this this email registered."
            except ProfileConfirmation.MultipleObjectsReturned:
                error_message = "You already sent too many confirmation emails. Something seems wrong. Please contact us at hello@getpushmonkey.com"

    else:
        form = ResendConfirmForm()
    return render_to_response('clients/resend-confirm.html', 
                              {'form': form, 'error_message': error_message, 'resent': resent}, 
                              RequestContext(request))

@csrf_exempt
@require_http_methods(["POST"])
def get_website_push_id(request):
    account_key = request.POST.get('account_key', None)
    response_data = {'website_push_id': ''}
    if account_key:
        try:
            profile = ClientProfile.objects.get(status = 'active', account_key = account_key)
            response_data = {
                'website_push_id': profile.website_push_id,
            }
        except ClientProfile.DoesNotExist:
            try:
                package = PushPackage.objects.get(identifier = account_key)
                response_data = {
                    'website_push_id': package.website_push_id,
                }
            except:
                raise Exception('No push package found for identifier (or profile for account key): ' + account_key)
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def icon_upload(request):
    profile = ClientProfile.objects.get(user = request.user)
    try:
        profile_image = ProfileImage.objects.get(profile = profile)
    except ProfileImage.DoesNotExist:
        profile_image = None
    success = False
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES)
        if form.is_valid():
            new_profile_image = form.save(commit = False)
            if profile_image:
                profile_image.image = new_profile_image.image
                profile_image.save()
            else:
                new_profile_image.profile = profile
                new_profile_image.save()
                profile_image = new_profile_image
            success = True
    else:
        form = ProfileImageForm()
    return render_to_response('clients/icon-upload.html', 
                              {'form': form,
                               'profile': profile,
                               'profile_image': profile_image,
                               'success': success,
                              }, 
                              RequestContext(request))

def customise(request):
    profile_id = request.GET.get('profile_id', '')
    try:
        profile = ClientProfile.objects.get(id = profile_id)
        print(profile.registration_step)
        if profile.registration_step > 2:
            raise Http404("Wrong user for profile_id=" + str(profile_id))
        profile.registration_step = 2
        profile.save()
    except:
        raise Http404("Reached customise with no ClientProfile. profile_id=" + str(profile_id))
    profile_image = None
    try:
        profile_image = ProfileImage.objects.get(profile = profile)
    except:
        pass
    if request.method == 'POST':
        form = CustomiseForm(request.POST)
        if form.is_valid():
            profile.website = form.cleaned_data.get('website_url', '')
            profile.website_name = form.cleaned_data.get('website_name', '')
            profile.save()
            if profile.from_envato:
                return redirect('register_thank_you', profile_id = profile.id) 
            return redirect('overview', profile_id = profile.id) 
    else :
        form = CustomiseForm(initial = {
            'profile_id': profile_id,
            'website_name': profile.website_name,
            'website_url': profile.website,
        })
    placeholder_profile_image_url = settings.STATIC_URL + "web.com.rhcloud.wptest-pushmonkey/pushPackage/iconset/icon_32x32.png"
    return render_to_response('clients/customise.html', 
                              {'form': form,
                               'placeholder_profile_image_url': placeholder_profile_image_url,
                               'profile': profile,
                               'profile_image': profile_image,
                              }, 
                              RequestContext(request))

def overview(request, profile_id = None):
    overview_pricing_tabel = True
    try: 
        profile = ClientProfile.objects.get(id = profile_id)
        if profile.registration_step != 2:

            raise Http404("Wrong profile.")
        profile.registration_step = 3
        profile.save()
    except:
        raise Http404("Wrong profile.")
    user = profile.user
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    if user:
        if user.is_active:
            auth_login(request, user)
    return render_to_response('clients/overview.html', 
                              { 
                                  'overview_pricing_tabel': overview_pricing_tabel,
                                  'prices': prices,
                                  'plans': plans,
                                  'profile': profile,
                              }, 
                              RequestContext(request))

@login_required
def dashboard(request):
    profile = ClientProfile.objects.get(user = request.user) 

    #force image upload step if not done before
    image = None
    try:
        image = ProfileImage.objects.get(profile = profile)
    except ProfileImage.DoesNotExist:
        return redirect('icon_upload')

    if request.GET.get('change_plan'):
        profile.preselected_plan = ''
        profile.save()

    wants_to_upgrade = False
    if request.GET.get('upgrade_plan', False):
        wants_to_upgrade = True
    account_key = profile.account_key
    notifications = PushMessage.objects.filter(account_key = account_key).count()
    subscribers = Device.objects.filter(account_key = account_key).count()
    sent_notifications = PushMessage.objects.sent_notifications_count(account_key = account_key)
    #sent_notifications = 1300000
    number_of_days = 20
    sent_notifications_dataset, opened_notifications_dataset = \
            PushMessage.objects.sent_and_opened_datasets(number_of_days = number_of_days, 
                                                         account_key = account_key)
    #sent_notifications_dataset = [random.randint(60, 100) for i in range(0, number_of_days)]
    #opened_notifications_dataset = [random.randint(30, 60) for i in range(0, number_of_days)]

    labels_dataset = PushMessage.objects.labels_dataset(number_of_days = number_of_days)

    already_had_trial = Plan.objects.already_had_trial(request.user)
    plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(request.user)

    #use the modal layout
    modal_pricing_table = True

    remaining_notifications = 0
    if plan:
        remaining_notifications = plan.number_of_notifications - sent_notifications

    #has pre-selected plan
    has_preselected_plan = False
    plan_type = None
    plan_type_length = None
    if len(profile.preselected_plan):
        has_preselected_plan = True
        split = profile.preselected_plan.split('-')
        plan_type = split[0]
        plan_type_length = split[1].upper()
        if plan_type_length == 'M':
            plan_type_length = 'monthly'
        else:
            plan_type_length = 'yearly'
        if plan_type:
            plan_type = int(plan_type)

    return render_to_response('clients/dashboard.html', 
                              {'account_key': account_key,
                               'notifications':notifications, 
                               'subscribers': subscribers, 
                               'sent_notifications': sent_notifications,
                               'sent_notifications_dataset': sent_notifications_dataset,
                               'opened_notifications_dataset': opened_notifications_dataset,
                               'labels_dataset': labels_dataset,
                               'plans': PlanVariant,
                               'plan': plan,
                               'has_only_expired_plans': has_only_expired_plans,
                               'modal_pricing_table': modal_pricing_table,
                               'remaining_notifications': remaining_notifications,
                               'profile': profile,
                               'has_preselected_plan': has_preselected_plan,
                               'plan_type': plan_type,
                               'plan_type_length': plan_type_length,
                               'prices': prices,
                               'already_had_trial': already_had_trial,
                               'wants_to_upgrade': wants_to_upgrade,
                              }, 
                              RequestContext(request))

@login_required
def websites(request):
    plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(request.user)
    if not plan or not plan.is_pro():
        raise Http404("You don't have the Pro plan.")
    cluster, created = WebsiteCluster.objects.get_or_create(creator = request.user)
    profile = ClientProfile.objects.get(user = request.user)
    too_many_websites = False
    if cluster.website_set.count() >= settings.MAX_NUMBER_OF_WEBSITES_ON_PRO:
        too_many_websites = True
    if created:
        default_website = website_from_profile(profile, cluster)
    if request.method == "POST":
        form = WebsiteForm(request.POST, request.FILES)
        if form.is_valid():
            # create the website
            website = Website(
                website_url = form.cleaned_data.get('website_url'), 
                cluster = cluster, 
                website_name = form.cleaned_data.get('website_name')
                )
            website.save()
            # create the website icon
            website_icon = WebsiteIcon(website = website, image = form.cleaned_data.get('icon'))
            website_icon.save()
            # associate a push package
            package_manager = PushPackageManager()
            package = package_manager.get_push_package(profile)
            if package:
                package.generate_zip(website.website_name, 
                                     website.website_url,
                                     website_icon.image128_2x.path,
                                     website_icon.image128.path,
                                     website_icon.image32_2x.path,
                                     website_icon.image32.path,
                                     website_icon.image16_2x.path,
                                     website_icon.image16.path,
                                    )
                website.account_key = package.identifier
                website.save()
                package.used = True
                package.save()
            return HttpResponseRedirect(reverse('websites'))
    else:
        form = WebsiteForm()
    return render_to_response('clients/websites.html', 
            {"form": form,
             "cluster": cluster,
             'plan': plan,
             'too_many_websites': too_many_websites,
            }, 
            RequestContext(request))

@login_required
def websites_delete(request, website_id):
    website = Website.objects.get(id = website_id)
    account_key = website.account_key
    package = PushPackage.objects.get(identifier = account_key)
    package.prepare_for_reuse()
    website.delete()
    return HttpResponseRedirect(reverse('websites'))

@never_cache
def login(request):
    profile = False
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            profile = ClientProfile.objects.get(user = user)
            if profile.confirmed:
                auth_login(request, form.get_user())
                url = request.GET.get('next')
                if not url:
                    url = settings.LOGIN_REDIRECT_URL
                return redirect(url)
    else:
        request.session.set_test_cookie()
        form = AuthenticationForm(request)

    return render_to_response('clients/login.html', 
                              {'form': form, 
                               'profile': profile, 
                               'action_url': request.get_full_path(),
                              }, 
                              RequestContext(request))

def notification_icon(request, account_key = ''):
    try:
        profile = ClientProfile.objects.get(account_key = account_key)
    except ClientProfile.DoesNotExist:
        profile = None
    if profile:
        website_push_id = profile.website_push_id
    else:
        website_push_id = 'web.com.rhcloud.wptest-pushmonkey'
    try:
        profile_image = ProfileImage.objects.get(profile = profile)
        if os.path.exists(profile_image.image32.path):
            return redirect(profile_image.image32.url)
    except:
        pass
    return redirect(settings.STATIC_URL + website_push_id + '/pushPackage/iconset/icon_32x32.png')

def send_account_key(request, email = ''):
    try:
        profile = ClientProfile.objects.get(user__email = email)
    except ClientProfile.DoesNotExist:
        profile = None

    if profile:
        if not profile.status == 'active':
            return HttpResponse('The profile does not have the Active status. Please re-check')
        if not profile.confirmed:
            return HttpResponse('The profile is not confirmed. Please re-check')
        if not len(profile.website_push_id):
            return HttpResponse('The profile does not have an Website Push ID. Please re-check')
        if not len(profile.url_format_string):
            return HttpResponse('The profile does not have an URL Format. Please re-check')
        
        email_manager = ClientsEmailManager()
        email_manager.send_account_key_email(to_email = profile.user.email, 
                                             first_name = profile.user.first_name,
                                             account_key = profile.account_key)
        return HttpResponse('Email sent!')
    return HttpResponse('No profile associated to ' + email)

@csrf_exempt
@require_http_methods(["POST"])
def api_sign_in(request):
    username = request.POST.get('api_token', None)
    password = request.POST.get('api_secret', None)
    from_envato = request.POST.get('envato', None)
    website_url = request.POST.get('website_url', 'default')
    profile = None
    if username and password:
        user = authenticate(username = username, password = password)
        if user:
            try:
                profile = ClientProfile.objects.get(user = user, status = 'active')
                response_data = {
                    'signed_in': True,
                    'account_key': profile.account_key,
                    'email': profile.user.email,
                }
                plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(profile.user)
                if plan and plan.is_pro():
                    cluster, created = WebsiteCluster.objects.get_or_create(creator = profile.user)
                    if created:
                        website = website_from_profile(profile, cluster)
                    try:
                        clean = clean_website_url(website_url)
                        website = cluster.website_set.get(website_url__contains = clean)
                        response_data["account_key"] = website.account_key
                    except Website.DoesNotExist:
                        response_data["log"] = "No website found in cluster."
            except Exception, e:
                response_data = {
                    'error': "Your account has not been verified yet. Please try again later.",
                    'signed_in': False,
                }
        else:
            response_data = {
                'error': "Invalid email and password.",
                'signed_in': False,
            }
    else:
        account_key = request.POST.get('account_key', None)
        if account_key:
            try:
                profile = ClientProfile.objects.get(account_key = account_key)
                email = profile.user.email
            except ClientProfile.DoesNotExist:
                profile = None
                email = ''
            if profile:
                response_data = {
                    'signed_in': True,
                    'account_key': account_key,
                    'email': email,
                }
            else:
                response_data = {
                    'error': "Server Error",
                    'signed_in': False,
                }
        else:
            response_data = {
                'error': "Missing email, password or account key.",
                'signed_in': False,
            }
    if profile:
        plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(profile.user)
        if has_only_expired_plans and from_envato:
            plan = Plan.objects.create_fixed_plan(profile.user)
            response_data['transitioned_to_envato'] = True
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
@require_http_methods(["POST"])
def api_get_plan_name(request):
    account_key = request.POST.get('account_key', False)
    response_data = {}
    if not account_key:
        response_data = {
            'error': 'Account key required.'
        }
    else:
        is_in_cluster = False
        profiles = ClientProfile.objects.filter(account_key = account_key)
        if not profiles.count():
            try:
                website = Website.objects.get(account_key = account_key)
                is_in_cluster = True
                plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(website.cluster.creator)
                if plan:
                    response_data = {
                        'plan_name': plan.get_type_display(),
                        'can_upgrade': False,
                    }
                else:                
                    if has_only_expired_plans:
                        response_data = {
                            'expired': True,
                            'can_upgrade': False,
                        }
                    else:
                        response_data = { 
                            'error': 'No price plan selected',
                        }
            except Website.DoesNotExist:
                response_data = {
                    'error': 'Client account not found',
                }
        else:
            profile = ClientProfile.objects.get(account_key = account_key)
            plan, has_only_expired_plans = Plan.objects.get_current_plan_for_user(profile.user)
            if plan:
                response_data = {
                    'plan_name': plan.get_type_display(),
                    'can_upgrade': False,
                }
                if plan.is_trial():
                    response_data['can_upgrade'] = True
            else:
                if has_only_expired_plans:
                    response_data = {
                        'expired': True,
                        'can_upgrade': True,
                    }
                else:
                    response_data = {
                        'error': 'No price plan selected.',
                    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def api_is_expired(request):
    pass
