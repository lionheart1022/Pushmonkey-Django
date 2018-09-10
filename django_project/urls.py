from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

admin.autodiscover()

handler500 = 'django_project.views.server_error'

urlpatterns = patterns('',
  url(r'^push$', 'django_project.views.push', name='push'),
  url(r'^test$', 'django_project.views.test', name='test'),
  url(r'^push_message$', 'django_project.views.push_message', name='push_message'),
  url(r'^push/v1/log$', 'django_project.views.apn_log', name='apn_log'),
  url(r'^push/v1/pushPackages/(?P<website_push_id>.+)$', 'django_project.views.apn_push_package', name='apn_push_package'),
  url(r'^push/v1/devices/(?P<device_id>.+)/registrations/(?P<website_id>.+)$', 'django_project.views.apn_device_register', name='apn_device_register'),
  url(r'^report/daily_digest$', 'django_project.views.daily_digest_cron', name='daily_digest_cron'),
  #users
  url(r'^logout$', 'django.contrib.auth.views.logout', {'template_name': 'clients/register.html', 'next_page': '/login'}, name='logout'),
  url(r'^password_reset$', 'django.contrib.auth.views.password_reset', 
  {'template_name': 'clients/password-reset.html', 
  'email_template_name': 'clients/password-reset-email.html'}, 
  name='password_reset'),
  url(r'^password_reset_done$', 'django.contrib.auth.views.password_reset_done', 
  {'template_name': 'clients/password-reset-done.html'}, 
  name='password_reset_done'),
  url(r'^password_reset_confirm/(?P<uidb64>.+)/(?P<token>.+)$', 'django.contrib.auth.views.password_reset_confirm', 
  {'template_name': 'clients/password-reset-confirm.html'}, 
  name='password_reset_confirm'),
  url(r'^password_reset_complete$', 'django.contrib.auth.views.password_reset_complete', 
  {'template_name': 'clients/password-reset-complete.html'}, 
  name='password_reset_complete'),
  #
  # clients
  #
  url(r'^login$', 'clients.views.login', name="login"),
  url(r'^register$', 'clients.views.register', name='register'),
  url(r'^register/customise$', 'clients.views.customise', name='customise'),
  url(r'^register/overview/(?P<profile_id>.+)$', 'clients.views.overview', name='overview'),
  url(r'^register/thank-you/(?P<profile_id>.+)$', 'clients.views.register_thank_you', name='register_thank_you'),
  url(r'^register/plan/(?P<preselected_plan>.+)$', 'clients.views.register', name='register_preselected_plan'),
  url(r'^confirm/resend$', 'clients.views.resend_confirm', name='resend_confirm'),
  url(r'^confirm/(?P<confirmation_key>.+)$', 'clients.views.register_confirm', name='register_confirm'),
  url(r'^dashboard$', 'clients.views.dashboard', name='dashboard'),
  url(r'^dashboard/icon_upload$', 'clients.views.icon_upload', name='icon_upload'),
  url(r'^dashboard/website_icon_upload/(?P<website_id>.+)$', 'clients.views.website_icon_upload', name='website_icon_upload'),  
  # multiple website management
  url(r'^dashboard/websites$', 'clients.views.websites', name='websites'),                     
  url(r'^dashboard/websites/delete/(?P<website_id>.+)$', 'clients.views.websites_delete', name='websites_delete'),
  url(r'^dashboard/websites/resend/(?P<website_id>.+)$', 'clients.views.websites_resend_invitation', name='websites_resend_invitation'),
  url(r'^register_agent/(?P<invitation_id>.+)$', 'clients.views.website_register_agent', name='website_register_agent'),
  url(r'^accept/(?P<invitation_id>.+)$', 'clients.views.website_invitation_accept', name='website_invitation_accept'),  
  # API
  url(r'^clients/get_website_push_id$', 'clients.views.get_website_push_id', name='get_website_push_id'),
  url(r'^clients/icon/(?P<account_key>.+)$', 'clients.views.notification_icon', name='notification_icon'),
  url(r'^clients/send_account_key/v2/(?P<email>.+)$', 'clients.views.send_account_key', name='send_account_key'),
  url(r'^uploads/', include('django_jfu_pushmonkey.urls')),
  url(r'^clients/api/sign_in$', 'clients.views.api_sign_in', name='api_sign_in'),
  url(r'^clients/api/get_plan_name$', 'clients.views.api_get_plan_name', name='api_get_plan_name'),
  url(r'^clients/api/is_expired$', 'clients.views.api_is_expired', name='api_is_expired'),
  #
  #stats
  #
  url(r'^stats/$', 'stats.views.stats', name='stats'),
  url(r'^stats/api$', 'stats.views.stats_api', name='stats_api'),
  url(r'^stats/track_open/(?P<push_message_id>.+)$', 'stats.views.track', name='track_open'),
  url(r'^stats/(?P<account_key>.+)$', 'stats.views.stats', name='stats'),
  #
  #plans
  #
  url(r'^plans/payment_overview/(?P<type>.+)/(?P<selected_plan>.+)/coupon/(?P<coupon_id>.+)$', 
  'plans.views.payment_overview', 
  name='payment_overview_coupon'),
  url(r'^plans/payment_overview/(?P<type>.+)/(?P<selected_plan>.+)$', 'plans.views.payment_overview', name='payment_overview'),
  url(r'^plans/payment/apply_coupon$', 'plans.views.payment_apply_coupon', name='payment_apply_coupon'),
  url(r'^plans/trial/thank_you$', 'plans.views.trial_thank_you', name='trial_thank_you'),
  #
  #paypal
  #
  (r'^plans/paypal/', include('paypal.standard.ipn.urls')),
  url(r'^plans/paypal/payment_processing/(?P<selected_plan>.+)$', 'plans.views.payment_processing', name='payment_processing'),
  url(r'^plans/paypal/payment_cancelled$', 'plans.views.payment_cancelled', name='payment_cancelled'),
  #
  #coupons
  #
  url(r'^coupons/redeem$', 'coupons.views.redeem', name='redeem_coupon'),
  #
  #pages
  #
  url(r'^terms-and-conditions', TemplateView.as_view(template_name='tc.html'), name='tc'),
  url(r'^privacy-policy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
  url(r'^404', TemplateView.as_view(template_name='404.html'), name='page_404'),
  url(r'^500', TemplateView.as_view(template_name='500.html'), name='page_500'),
  url(r'^help', TemplateView.as_view(template_name='help.html'), name='help'),
  url(r'^team', TemplateView.as_view(template_name='team.html'), name='team'),
  url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt'), name='robots'),
  url(r'^sitemap.xml$', TemplateView.as_view(template_name='sitemap.xml'), name='sitemap'),
  url(r'^favicon.ico$', RedirectView.as_view(url='/static/images/favicon.ico'), name='favicon'),
  url(r'^apple-touch-icon.png$', RedirectView.as_view(url='/static/images/push-monkey-logo-60x60.png'), name='apple-touch-icon'),
  url(r'^apple-touch-icon-precomposed.png$', RedirectView.as_view(url='/static/images/push-monkey-logo-60x60.png'), name='apple-touch-icon-precomposed'),
  url(r'^changelog/fixed', TemplateView.as_view(template_name='changelog_fixed.html'), name='changelog_fixed'),
  url(r'^changelog/wordpress', TemplateView.as_view(template_name='changelog_wordpress.html'), name='changelog_wordpress'),
  #
  # service workers
  #
  url(r'^chrome', TemplateView.as_view(template_name='chrome/index.html')),
  url(r'^push/v1/register/(?P<account_key>.+)', 'pushmonkey.views.register', name='service_worker_register'),
  url(r'^push/v1/unregister/(?P<subscription_id>.+)', 'pushmonkey.views.unregister', name='service_worker_unregister'),  
  url(r'^push/v1/notifs/(?P<account_key>.+)', 'pushmonkey.views.notifications', name='service_worker_notifications'),                     
  url(r'^push/v1/resend_demo/(?P<account_key>.+)', 'pushmonkey.views.resend_demo', name='service_worker_resend_demo'),
  url(r'^(?P<account_key>.+)/service-worker.js$', 'pushmonkey.views.service_worker', name='service_worker_js'),
  url(r'^service-worker-(?P<account_key>.+).php$', 'pushmonkey.views.service_worker', name='service_worker_php'),
  url(r'^(?P<account_key>.+)/manifest.json$', 'pushmonkey.views.manifest', name='manifest'),
  url(r'^manifest-(?P<account_key>.+).json$', 'pushmonkey.views.manifest', name='manifest_alt'),  
  url(r'^sdk/config-(?P<account_key>.+).js$', 'pushmonkey.views.config_js', name='config_js'),
  url(r'^sdk/sdk-(?P<account_key>.+).js$', 'pushmonkey.views.sdk_js', name='sdk_js'),  
  url(r'^(?P<account_key>.+)/register-service-worker$', 'pushmonkey.views.register_service_worker', name='register_service_worker'),  

  #
  # segments
  #
  url(r'^push/v1/segments/delete/(?P<account_key>.+)$', 'segments.views.delete_segment', name='delete_segment'),    
  url(r'^push/v1/segments/create/(?P<account_key>.+)$', 'segments.views.create_segment', name='create_segment'),  
  url(r'^push/v1/segments/save/(?P<account_key>.+)$', 'segments.views.save_segments', name='save_segments'),  
  url(r'^push/v1/segments/(?P<account_key>.+)$', 'segments.views.segments', name='segments'),  
  # in Dashboard
  url(r'^dashboard/segmentation/delete/(?P<id>.+)$', 'segments.views.delete', name='segments_delete'),  
  url(r'^dashboard/segmentation$', 'segments.views.dashboard', name='segments_dashboard'),  

  # TODO: handle unregister
  #affiliates
  url(r'^af/', include('affiliates.urls')),
  # Examples:
  url(r'^$', 'django_project.views.home', name='home'),
  url(r'^banner/', TemplateView.as_view(template_name='banner.html'), name='banner'),
  url(r'^banner-mobile/', TemplateView.as_view(template_name='banner-mobile.html'), name='banner-mobile'),
  url(r'^banner-smobile/', TemplateView.as_view(template_name='banner-smobile.html'), name='banner-smobile'),  
  url(r'^admin/', include(admin.site.urls)),
)

if settings.IS_LOCAL:
  # media files 
  urlpatterns += patterns('',
  (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))

