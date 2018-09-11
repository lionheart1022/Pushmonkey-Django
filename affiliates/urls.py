from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, RedirectView

urlpatterns = patterns('affiliates.views',
                       url(r'^join$', 'join', name="affiliates_join"),
                       url(r'^center$', 'center', name="affiliates_center"),
                       url(r'^request_payout$', 'request_payout', name="request_payout"),
                       url(r'^(?P<token>[A-Z0-9]{6})$', 'track', name='affiliates_track'),
                      )

additional_patterns = patterns('',
                               url(r'^terms-and-conditions', TemplateView.as_view(template_name='affiliates/terms.html'), name='affiliates_terms'),
                              )

urlpatterns += additional_patterns
