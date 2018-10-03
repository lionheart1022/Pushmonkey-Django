from django.contrib import admin
from models import Plan

class PlanAdmin(admin.ModelAdmin):
    list_filter = ('user', 'type' )
    list_display = ('user', 'get_type_display', 'created_at', 'payed', 'status')
admin.site.register(Plan, PlanAdmin)
