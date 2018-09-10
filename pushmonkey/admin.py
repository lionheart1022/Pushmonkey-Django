from django.contrib import admin
from models import Device, PushMessage, PushPackage, Batch, WebServiceDevice


class WebServiceDeviceAdmin(admin.ModelAdmin):
  search_fields = ['account_key', 'subscription_id', 'endpoint']
  list_display = ('subscription_id', 'endpoint', 'created_at', 'account_key', 'comment', 'mozilla', 'chrome')
  list_filter = ('tested',)
admin.site.register(WebServiceDevice, WebServiceDeviceAdmin)

class DeviceAdmin(admin.ModelAdmin):
    list_filter = ('account_key',)
    list_display = ('token', 'account_key', 'ported', 'comment')
    search_fields = ['token']
admin.site.register(Device, DeviceAdmin)

class PushMessageAdmin(admin.ModelAdmin):
    list_filter = ('account_key',)
    list_display = ('title', 'account_key', 'device_num', 'opened_num', 'comment', 'custom')
    readonly_fields = ['segments']
admin.site.register(PushMessage, PushMessageAdmin)

class PushPackageAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'website_push_id', 'used', 'website_push_id_created', 'created_at', 'updated_at')
    list_editable = ('website_push_id_created', )
    search_fields = ['identifier']
admin.site.register(PushPackage, PushPackageAdmin)

class BatchAdmin(admin.ModelAdmin):
    list_display = ('push_message', 'created_at', 'updated_at')
admin.site.register(Batch, BatchAdmin)
