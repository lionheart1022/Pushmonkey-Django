from django.conf.urls import patterns, include, url

urlpatterns = patterns('django_jfu_pushmonkey.views',
                       url( r'icon-upload$', 'upload', name = 'jfu_upload' ),
                      )
