from django.contrib import admin
from models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'created_at')
    list_filter = ('email',  'name')
admin.site.register(Message, MessageAdmin)
