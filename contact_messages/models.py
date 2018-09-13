from datetime import datetime
from django.db import models

class Message(models.Model):
    email = models.EmailField(max_length = 200)
    name = models.CharField(max_length = 200)
    message = models.TextField(max_length = 900)
    created_at = models.DateTimeField(default = datetime.now)
    updated_at = models.DateTimeField(auto_now = True, default = datetime.now)

    def __unicode__(self):
        return self.email
