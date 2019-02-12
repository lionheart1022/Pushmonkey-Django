# -*- coding: utf-8 -*-
# Django settings for OpenShift project.
import imp, os

# a setting to determine whether we are running on OpenShift
ON_OPENSHIFT = False
if os.environ.has_key('OPENSHIFT_REPO_DIR'):
    ON_OPENSHIFT = True

# the ID of the app on the OpenShift server. Used in a few situations, e.g. creating the path to the logs or the path to the Django command
# to send push notifications in the background, with a delay.
#OPENSHIFT_ID = "540456a05973ca475300013e" #live
OPENSHIFT_ID = os.environ.get('OPENSHIFT_APP_UUID')

# This is the OpenShift user ID for staging 
ON_LIVE = True
if OPENSHIFT_ID == '5458e5f2e0b8cd35710004e4':
    ON_LIVE = False

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
if ON_OPENSHIFT:
    DEBUG = bool(os.environ.get('DEBUG', False))
    if DEBUG:
        print("WARNING: The DEBUG environment is set to True.")
else:
    DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tudor Munteanu', 'tudor@mowowstudios.com'),
)

MANAGERS = (
    ('Tudor Munteanu', 'tudor@mowowstudios.com'),
    ('Ash K', 'tudor@getpushmonkey.com'),
)

if ON_OPENSHIFT:
    if ON_LIVE:
        # os.environ['OPENSHIFT_MYSQL_DB_*'] variables can be used with databases created
        # with rhc cartridge add (see /README in this git repo)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'magic',  # Or path to database file if using sqlite3.
                'USER': 'admintb215n9',                      # Not used with sqlite3.
                'PASSWORD': 'z5Ptx1LgnG_8',                  # Not used with sqlite3.
                'HOST': os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': os.environ['OPENSHIFT_POSTGRESQL_DB_PORT'],                      # Set to empty string for default. Not used with sqlite3.
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'dev',  # Or path to database file if using sqlite3.
                'USER': 'admin3wrgmtn',                      # Not used with sqlite3.
                'PASSWORD': 'nDfuyZYJJ4JA',                  # Not used with sqlite3.
                'HOST': os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': os.environ['OPENSHIFT_POSTGRESQL_DB_PORT'],                      # Set to empty string for default. Not used with sqlite3.
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.path.join(PROJECT_DIR, 'sqlite3.db'),  # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR', ''), 'media')
if not ON_OPENSHIFT:
    MEDIA_ROOT = os.path.join(PROJECT_DIR, '..', '..', '..', '..', 'magic-media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/media/'
if not ON_OPENSHIFT:
    MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, '..', 'static')
# In development, the STATIC_ROOT should be empty, while STATICFILES_DIRS should
# contain the full disk path to the /static dir which is outside the project
if not ON_OPENSHIFT:
    STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
if not ON_OPENSHIFT:
    STATICFILES_DIRS = ( os.path.join(PROJECT_DIR, '..', 'static'),)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make a dictionary of default keys
default_keys = { 'SECRET_KEY': 'vm4rl5*ymb@2&d_(gc$gb-^twq9w(u69hi--%$5xrh!xk(t%hw' }

# Replace default keys with dynamic values if we are in OpenShift
use_keys = default_keys
if ON_OPENSHIFT:
    imp.find_module('openshiftlibs')
    import openshiftlibs
    use_keys = openshiftlibs.openshift_secure(default_keys)

# Make this unique, and don't share it with anybody.
SECRET_KEY = use_keys['SECRET_KEY']

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pushmonkey.middleware.cors.XsSharing'
)

ROOT_URLCONF = 'openshift.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'plans.context_processors.should_show_black_friday_banner',
    'plans.context_processors.should_show_cool_update_banner',
) 

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ## Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.humanize',
    'paypal.standard.ipn',
    'djacobs_apns',
    'pushmonkey',
    'south',
    'clients',
    'stats',
    'backup',
    'plans',
    'coupons',
    'emails',
    'contact_messages',
    'affiliates',
    'django_jfu_pushmonkey',
    'imagekit',
    'django_push_package',
    'website_clusters'
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
)

AUTHENTICATION_BACKENDS = ('clients.backends.EmailAuthBackend',)

# Email Config
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.socketlabs.com'
EMAIL_HOST_USER = 'server14980'
EMAIL_HOST_PASSWORD = 'Ax9o2E4Fsb6K7Qi'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'Push Monkey <mailer@getpushmonkey.com>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Auth
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/dashboard"

# ImageKit
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'

# PayPal
PAYPAL_TEST = False
if PAYPAL_TEST:
    PAYPAL_RECEIVER_EMAIL = "payments-facilitator@getpushmonkey.com" #sandbox
else:
    PAYPAL_RECEIVER_EMAIL = "payments@getpushmonkey.com" #production
PAYPAL_SUBSCRIPTION_IMAGE = "/static/images/paypal-button.png"
PAYPAL_SUBSCRIPTION_SANDBOX_IMAGE = "/static/images/paypal-button.png"

# Max number of website for Pro plan
MAX_NUMBER_OF_WEBSITES_ON_PRO = 5

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'DEBUG',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'djacobs_apns.apns': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
