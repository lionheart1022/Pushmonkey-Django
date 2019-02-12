from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
import os
from datetime import datetime
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        today = datetime.today().strftime("%Y-%m-%d")
        subject = 'Push Monkey Backup for ' + today
        body = 'Find the database dump attached'
        emails = [person[1] for person in settings.MANAGERS]
        email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, emails)
        path = os.environ['OPENSHIFT_DATA_DIR'] + 'dump-' + today + '.json'
        email.attach_file(path)
        email.send(fail_silently=False)
