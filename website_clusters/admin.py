from django.contrib import admin
from models import WebsiteCluster, Website, WebsiteIcon, WebsiteInvitation


class WebsiteAdmin(admin.ModelAdmin):
	list_display = ('website_url', 'account_key', 'cluster', 'created_at')
admin.site.register(Website, WebsiteAdmin)

class WebsiteInvitationAdmin(admin.ModelAdmin):
  list_display = ('website', 'email', 'created_at', 'updated_at', 'accepted')  
admin.site.register(WebsiteInvitation, WebsiteInvitationAdmin)

admin.site.register(WebsiteCluster)
admin.site.register(WebsiteIcon)
