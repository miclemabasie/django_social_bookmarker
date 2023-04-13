from django import forms


class LoginForm(forms.Forms):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    password = forms.CharField(widget=forms.PasswordInput)
