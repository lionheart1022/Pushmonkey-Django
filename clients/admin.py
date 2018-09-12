from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from models import ClientProfile, ProfileConfirmation, ProfileImage
from pushmonkey.models import PushPackage
import csv

class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_first_name', 'website', 'account_key', 'confirmed', 'status', 'has_push_package', 'created_at', 'from_envato')
    list_filter = ('confirmed',  )
    actions = ['assign_push_package']
    search_fields = ['account_key', 'user__email']

    def user_first_name(self, obj):
      return obj.user.first_name
    user_first_name.short_description = 'First name'

    def assign_push_package(self, request, queryset):
        profiles_count = queryset.count()
        push_packages_count = PushPackage.objects.filter(used = False, website_push_id_created = True).count()
        if profiles_count > push_packages_count:
            messages.error(request, "Not enough Push Packages are available for all the selected profiles." + 
                             "You might need to create more Push Packages.")
            return
        for profile in queryset.all():
            #TODO: send user email to let him know
            try:
                profile_image = ProfileImage.objects.get(profile = profile)
            except:
                messages.error(request, profile.user.email + " does not have an icon uploaded.")
                return
            package = PushPackage.objects.filter(used = False, website_push_id_created = True)[0]
            package.generate_zip(profile.website_name, 
                                 profile.website,
                                 profile_image.image128_2x.path,
                                 profile_image.image128.path,
                                 profile_image.image32_2x.path,
                                 profile_image.image32.path,
                                 profile_image.image16_2x.path,
                                 profile_image.image16.path,
                                )
            profile.status = 'active'
            profile.account_key = package.identifier
            profile.website_push_id = package.website_push_id
            profile.save()
            package.used = True
            package.save()
        rows_updated = queryset.count()
        if rows_updated == 1:
            message_bit = "1 profile was"
        else:
            message_bit = "%s profiles were" % rows_updated
        self.message_user(request, "%s successfully assigned a Push Package." % message_bit)
    assign_push_package.short_description = "Assign a push package"

    def get_urls(self):
      urls = super(ClientProfileAdmin, self).get_urls()
      custom_urls = [
          url(r'^export/$', self.export),
      ]
      return custom_urls + urls

    def export(self, request):
        if not request.user.is_staff:
            raise PermissionDenied
        queryset = ClientProfile.objects.all()
        opts = queryset.model._meta
        model = queryset.model
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment;filename=export.csv'
        writer = csv.writer(response)
        field_names = [field.name for field in opts.fields]
        writer.writerow(field_names)
        for obj in queryset:
          row = []
          for field in field_names:
            try:
              row.append(getattr(obj, field).encode("utf-8"))
            except:
              row.append(getattr(obj, field))
          writer.writerow(row)
        return response

admin.site.register(ClientProfile, ClientProfileAdmin)

admin.site.register(ProfileConfirmation)
admin.site.register(ProfileImage)
