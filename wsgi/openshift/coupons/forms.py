from django import forms
from models import Coupon
from datetime import datetime

class RedeemForm(forms.Form):
    code = forms.CharField()

    def clean(self):
        cleaned_data = super(RedeemForm, self).clean()
        try:
            #coupon = Coupon.objects.get(string = cleaned_data.get('code'), redeemed = False)
            coupon = Coupon.objects.get(string = cleaned_data.get('code'), redeemed = False, end_at__gt = datetime.now())
        except:
            raise forms.ValidationError("This doesn't seem to be a valid coupon code.")
        return cleaned_data
