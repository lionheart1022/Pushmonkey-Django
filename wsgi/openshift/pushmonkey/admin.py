from django.contrib import admin
from models import Device, PushMessage, PushPackage, Batch, WebServiceDevice

admin.site.register(WebServiceDevice)

class DeviceAdmin(admin.ModelAdmin):
    list_filter = ('account_key',)
    list_display = ('token', 'account_key', 'ported', 'comment')
    search_fields = ['token']
admin.site.register(Device, DeviceAdmin)

class PushMessageAdmin(admin.ModelAdmin):
    list_filter = ('account_key',)
    list_display = ('title', 'account_key', 'device_num', 'opened_num', 'comment', 'custom')
admin.site.register(PushMessage, PushMessageAdmin)

class PushPackageAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'website_push_id', 'used', 'website_push_id_created', 'created_at', 'updated_at')
    list_editable = ('website_push_id_created', )
    search_fields = ['identifier']
admin.site.register(PushPackage, PushPackageAdmin)

class BatchAdmin(admin.ModelAdmin):
    list_display = ('push_message', 'created_at', 'updated_at')
admin.site.register(Batch, BatchAdmin)
