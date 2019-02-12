from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler500 = 'openshift.views.server_error'

urlpatterns = patterns('',
  url(r'^push$', 'openshift.views.push', name='push'),
  url(r'^test$', 'openshift.views.test', name='test'),
  url(r'^push_message$', 'openshift.views.push_message', name='push_message'),
  url(r'^push/v1/log$', 'openshift.views.apn_log', name='apn_log'),
  url(r'^push/v1/pushPackages/(?P<website_push_id>.+)$', 'openshift.views.apn_push_package', name='apn_push_package'),
  url(r'^push/v1/devices/(?P<device_id>.+)/registrations/(?P<website_id>.+)$', 'openshift.views.apn_device_register', name='apn_device_register'),
  url(r'^report/daily_digest$', 'openshift.views.daily_digest_cron', name='daily_digest_cron'),
  #users
  url(r'^logout$', 'django.contrib.auth.views.logout', {'template_name': 'clients/register.html', 'next_page': '/login'}, name='logout'),
  url(r'^password_reset$', 'django.contrib.auth.views.password_reset', 
  {'template_name': 'clients/password-reset.html', 
  'email_template_name': 'clients/password-reset-email.html'}, 
  name='password_reset'),
  url(r'^password_reset_done$', 'django.contrib.auth.views.password_reset_done', 
  {'template_name': 'clients/password-reset-done.html'}, 
  name='password_reset_done'),
  url(r'^password_reset_confirm/(?P<uidb36>.+)/(?P<token>.+)$', 'django.contrib.auth.views.password_reset_confirm', 
  {'template_name': 'clients/password-reset-confirm.html'}, 
  name='password_reset_confirm'),
  url(r'^password_reset_complete$', 'django.contrib.auth.views.password_reset_complete', 
  {'template_name': 'clients/password-reset-complete.html'}, 
  name='password_reset_complete'),
  #clients
  url(r'^login$', 'openshift.clients.views.login', name="login"),
  url(r'^register$', 'openshift.clients.views.register', name='register'),
  url(r'^register/customise$', 'openshift.clients.views.customise', name='customise'),
  url(r'^register/overview/(?P<profile_id>.+)$', 'openshift.clients.views.overview', name='overview'),
  url(r'^register/thank-you/(?P<profile_id>.+)$', 'openshift.clients.views.register_thank_you', name='register_thank_you'),
  url(r'^register/plan/(?P<preselected_plan>.+)$', 'openshift.clients.views.register', name='register_preselected_plan'),
  url(r'^confirm/resend$', 'openshift.clients.views.resend_confirm', name='resend_confirm'),
  url(r'^confirm/(?P<confirmation_key>.+)$', 'openshift.clients.views.register_confirm', name='register_confirm'),
  url(r'^dashboard$', 'openshift.clients.views.dashboard', name='dashboard'),
  url(r'^dashboard/icon_upload$', 'openshift.clients.views.icon_upload', name='icon_upload'),
  url(r'^dashboard/websites$', 'openshift.clients.views.websites', name='websites'),                     
  url(r'^dashboard/websites/delete/(?P<website_id>.+)$', 'openshift.clients.views.websites_delete', name='websites_delete'),                                            
  url(r'^clients/get_website_push_id$', 'openshift.clients.views.get_website_push_id', name='get_website_push_id'),
  url(r'^clients/icon/(?P<account_key>.+)$', 'openshift.clients.views.notification_icon', name='notification_icon'),
  url(r'^clients/send_account_key/v2/(?P<email>.+)$', 'openshift.clients.views.send_account_key', name='send_account_key'),
  url(r'^uploads/', include('django_jfu_pushmonkey.urls')),
  url(r'^clients/api/sign_in$', 'openshift.clients.views.api_sign_in', name='api_sign_in'),
  url(r'^clients/api/get_plan_name$', 'openshift.clients.views.api_get_plan_name', name='api_get_plan_name'),
  url(r'^clients/api/is_expired$', 'openshift.clients.views.api_is_expired', name='api_is_expired'),
  #stats
  url(r'^stats/$', 'openshift.stats.views.stats', name='stats'),
  url(r'^stats/api$', 'openshift.stats.views.stats_api', name='stats_api'),
  url(r'^stats/track_open/(?P<push_message_id>.+)$', 'openshift.stats.views.track', name='track_open'),
  url(r'^stats/(?P<account_key>.+)$', 'openshift.stats.views.stats', name='stats'),
  #plans
  url(r'^plans/payment_overview/(?P<type>.+)/(?P<selected_plan>.+)/coupon/(?P<coupon_id>.+)$', 
  'openshift.plans.views.payment_overview', 
  name='payment_overview_coupon'),
  url(r'^plans/payment_overview/(?P<type>.+)/(?P<selected_plan>.+)$', 'openshift.plans.views.payment_overview', name='payment_overview'),
  url(r'^plans/payment/apply_coupon$', 'openshift.plans.views.payment_apply_coupon', name='payment_apply_coupon'),
  url(r'^plans/trial/thank_you$', 'openshift.plans.views.trial_thank_you', name='trial_thank_you'),
  #paypal
  (r'^plans/paypal/', include('paypal.standard.ipn.urls')),
  url(r'^plans/paypal/payment_processing/(?P<selected_plan>.+)$', 'openshift.plans.views.payment_processing', name='payment_processing'),
  url(r'^plans/paypal/payment_cancelled$', 'openshift.plans.views.payment_cancelled', name='payment_cancelled'),
  #coupons
  url(r'^coupons/redeem$', 'openshift.coupons.views.redeem', name='redeem_coupon'),
  #pages
  url(r'^terms-and-conditions', 'django.views.generic.simple.direct_to_template', {'template': 'tc.html'}, name='tc'),
  url(r'^privacy-policy', 'django.views.generic.simple.direct_to_template', {'template': 'privacy.html'}, name='privacy'),
  url(r'^404', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}, name='page_404'),
  url(r'^500', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}, name='page_500'),
  url(r'^help', 'django.views.generic.simple.direct_to_template', {'template': 'help.html'}, name='help'),
  url(r'^team', 'django.views.generic.simple.direct_to_template', {'template': 'team.html'}, name='team'),
  url(r'^robots.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'robots.txt'}, name='robots'),
  url(r'^sitemap.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'sitemap.xml'}, name='sitemap'),
  url(r'^D3FE892048C257252C7C6EA9FB8B6F35.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'D3FE892048C257252C7C6EA9FB8B6F35.txt'}, name='ssl-check'),
  url(r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}, name='favicon'),
  url(r'^apple-touch-icon.png$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/push-monkey-logo-60x60.png'}, name='apple-touch-icon'),
  url(r'^apple-touch-icon-precomposed.png$', 'django.views.generic.simple.redirect_to', 
  {'url': '/static/img/push-monkey-logo-60x60.png'}, name='apple-touch-icon-precomposed'),
  url(r'^changelog/fixed', 'django.views.generic.simple.direct_to_template', {'template': 'changelog_fixed.html'}, name='changelog_fixed'),
  url(r'^changelog/wordpress', 'django.views.generic.simple.direct_to_template', {'template': 'changelog_wordpress.html'}, name='changelog_wordpress'),
  # chrome
  url(r'^chrome', 'django.views.generic.simple.direct_to_template', {'template': 'chrome/index.html'}),
  url(r'^push/v1/register/(?P<account_key>.+)', 'openshift.pushmonkey.views.register', name='service_worker_register'),
  url(r'^push/v1/unregister/(?P<subscription_id>.+)', 'openshift.pushmonkey.views.unregister', name='service_worker_unregister'),  
  url(r'^push/v1/notifs/(?P<account_key>.+)', 'openshift.pushmonkey.views.notifications', name='service_worker_notifications'),                     
  url(r'^(?P<account_key>.+)/service-worker.js$', 'openshift.pushmonkey.views.service_worker', name='service_worker_js'),
  url(r'^(?P<account_key>.+)/manifest.json$', 'openshift.pushmonkey.views.manifest', name='manifest'),
  url(r'^sdk/config-(?P<account_key>.+).js$', 'openshift.pushmonkey.views.config_js', name='config_js'),
  url(r'^sdk/sdk.js$', 'openshift.pushmonkey.views.sdk_js', name='sdk_js'),  
  url(r'^(?P<account_key>.+)/register-service-worker$', 'openshift.pushmonkey.views.register_service_worker', name='register_service_worker'),  
  # TODO: handle unregister
  #affiliates
  url(r'^af/', include('affiliates.urls')),
  # Examples:
  url(r'^$', 'openshift.views.home', name='home'),
  url(r'^banner/', 'django.views.generic.simple.direct_to_template', {'template': 'banner.html'}, name='banner'),
  url(r'^banner-mobile/', 'django.views.generic.simple.direct_to_template', {'template': 'banner-mobile.html'}, name='banner-mobile'),
  url(r'^banner-smobile/', 'django.views.generic.simple.direct_to_template', {'template': 'banner-smobile.html'}, name='banner-smobile'),
  # url(r'^openshift/', include('openshift.foo.urls')),
  # Uncomment the admin/doc line below to enable admin documentation:
  # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  # Uncomment the next line to enable the admin:
  url(r'^admin/', include(admin.site.urls)),
)

if not settings.ON_OPENSHIFT:
  # media files 
  urlpatterns += patterns('',
  (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))