from django.contrib import admin
from models import Coupon, DiscountCoupon

class CouponAdmin(admin.ModelAdmin):
    list_filter = ('redeemed', )
    list_display = ('string', 'redeemed', 'user', 'admin_plan')
admin.site.register(Coupon, CouponAdmin)

class DiscountCouponAdmin(admin.ModelAdmin):
    list_filter = ('valid', )
    list_display = ('string', 'valid', 'single_use', 'user')
admin.site.register(DiscountCoupon, DiscountCouponAdmin)
