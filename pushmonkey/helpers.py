from django.conf import settings
from pushmonkey.models import PushMessage
import subprocess

def is_demo_account(account_key):

  return account_key == settings.DEMO_ACCOUNT_KEY

def send_demo_notification(account_key):

  message = PushMessage(title = "Welcome to Push Monkey", 
    body = "Keep your readers engaged.", 
    url_args = "",
    account_key = account_key, 
    custom = "", 
    comment = "")
  message.save()
  message_id = message.id
  subprocess.Popen("sleep 10; python " + settings.SUBPROCESS_COMMAND_PATH  + " " + str(message_id), shell=True)

