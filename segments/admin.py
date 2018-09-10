from django.contrib import admin
from models import Segment
from pushmonkey.models import Device, WebServiceDevice

class SegmentAdmin(admin.ModelAdmin):
  readonly_fields = ['device', 'web_service_device']
  search_fields = ['account_key', 'name']
  def formfield_for_manytomany(self, db_field, request, **kwargs):
    if db_field.name == "device":
      pk = self.get_pk(request)
      if pk:
        segment = Segment.objects.get(id = pk)
        kwargs["queryset"] = segment.device.all()
      else:
        kwargs["queryset"] = Device.objects.all()
    elif db_field.name == "web_service_device":
      pk = self.get_pk(request)
      if pk:
        segment = Segment.objects.get(id = pk)
        kwargs["queryset"] = segment.web_service_device.all()
      else:
        kwargs["queryset"] = WebServiceDevice.objects.all()      
    return super(SegmentAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

  def get_pk(self, request):
    try:
      pk = request.META['PATH_INFO'].strip('/').split('/')[-1]
      return int(pk)
    except ValueError:
      return None  
admin.site.register(Segment, SegmentAdmin)