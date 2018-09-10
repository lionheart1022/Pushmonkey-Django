from clients.models import ClientProfile
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pushmonkey.managers import PushMonkeyEmailManager
from pushmonkey.models import PushMessage, Device, WebServiceDevice
import subprocess

class Command(BaseCommand):

  def handle(self, *args, **options):
    now = datetime.now().replace(second=0, microsecond=0)
    notifications = PushMessage.objects.filter(scheduled_at = now)
    command_path = settings.SUBPROCESS_COMMAND_PATH
    for n in notifications:
      subprocess.Popen("sleep 10; python " + command_path + " " + str(n.id), shell=True)
