from django import forms

CONTENT_TYPES = (
    (2, "Groups"),
    (3, "Users"),
    (7, "Sites"),
    (14, "Indices"),
    (15, "Social Links"),
    (19, "Configurations"),
    (20, "SEO Sites"),
    (21, "SEO Site Redirects"),
    (23, "Google Analytics"),
    (25, "Social Links"),
)


class ASLogin(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=30,
                               widget=forms.PasswordInput(render_value=False))

class ContentDropDown(forms.Form):
    content_type = forms.CharField(max_length=25,
                                   widget=forms.Select(choices=CONTENT_TYPES))
    