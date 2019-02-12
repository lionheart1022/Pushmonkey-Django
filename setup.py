#!/usr/bin/env python

from setuptools import setup

setup(
    name='PushMonkey',
    version='1.0',
    description='Enable Safari 7 Push Notifications (Mac OS Mavericks) on each new post published.',
    author='moWOW Studios',
    author_email='hey@mowowstudios.com',
    url='http://www.python.org/sigs/distutils-sig/',
    install_requires=['Django<=1.4', 'pyOpenSSL>=0.10', 'django-fields>=0.1.2', 'django-uuidfield', 'psycopg2', 'south', 'six', 'pillow', 'django-imagekit', 'requests'],
)
