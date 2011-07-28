from django import forms

from sawmill.conf import CONTENT_TYPES


class ASLogin(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=30,
                               widget=forms.PasswordInput(render_value=False))

class ContentDropDown(forms.Form):
    content_type = forms.CharField(max_length=25,
                                   widget=forms.Select(choices=CONTENT_TYPES))
    