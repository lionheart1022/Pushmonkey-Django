from django.db import models
from datetime import datetime

class Email(models.Model):
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)
    to_email = models.CharField(max_length = 100, default = '')
    subject = models.CharField(max_length = 200, default = '')

    def __unicode__(self):
        return self.to_email + ' - ' + self.subject
