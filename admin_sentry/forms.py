from django import forms

class ASLogin(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=30,
                               widget=forms.PasswordInput(render_value=False))
    