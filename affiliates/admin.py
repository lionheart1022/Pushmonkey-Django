from django.contrib import admin
from models import Affiliate, AffiliateLink, RegisteredUser, AffiliatePayment, Payout

admin.site.register(Affiliate)
admin.site.register(AffiliateLink)
admin.site.register(RegisteredUser)
class AffiliatePaymentAdmin(admin.ModelAdmin):
    list_display = ('item', 'payed_to_user')

    def item(self, obj):
        return str(obj)
admin.site.register(AffiliatePayment, AffiliatePaymentAdmin)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'honored')
admin.site.register(Payout, PayoutAdmin)
