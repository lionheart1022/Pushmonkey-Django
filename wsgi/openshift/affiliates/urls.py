from django.conf.urls import patterns, include, url

urlpatterns = patterns('affiliates.views',
                       url(r'^join$', 'join', name="affiliates_join"),
                       url(r'^center$', 'center', name="affiliates_center"),
                       url(r'^request_payout$', 'request_payout', name="request_payout"),
                       url(r'^(?P<token>[A-Z0-9]{6})$', 'track', name='affiliates_track'),
                      )

additional_patterns = patterns('',
                               url(r'^terms-and-conditions', 'django.views.generic.simple.direct_to_template', {'template': 'affiliates/terms.html'}, name='affiliates_terms'),
                              )

urlpatterns += additional_patterns
