from django.contrib import admin
from models import Email

class EmailAdmin(admin.ModelAdmin):
    list_display = ('to_email', 'subject')
    list_filter = ('to_email', )
admin.site.register(Email, EmailAdmin)
