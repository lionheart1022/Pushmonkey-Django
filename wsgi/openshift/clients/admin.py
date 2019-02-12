from django.contrib import admin
from django.contrib import messages
from models import ClientProfile, ProfileConfirmation, ProfileImage
from pushmonkey.models import PushPackage

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

admin.site.register(ClientProfile, ClientProfileAdmin)

admin.site.register(ProfileConfirmation)
admin.site.register(ProfileImage)
