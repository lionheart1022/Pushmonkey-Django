from django import forms

class SegmentForm(forms.Form):
    name = forms.CharField()

    def clean_name(self):
      return self.cleaned_data.get('name').capitalize()