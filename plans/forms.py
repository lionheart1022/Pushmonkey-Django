from django import forms

class DiscountCouponForm(forms.Form):
    coupon_string = forms.CharField(required = False)
    selected_plan = forms.CharField(widget = forms.HiddenInput)
    time_unit = forms.CharField(widget = forms.HiddenInput)
