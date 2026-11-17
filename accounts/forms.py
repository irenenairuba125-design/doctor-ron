from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

from core.forms import BootstrapFormMixin, BootstrapModelForm

from .models import User


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class UserCreateForm(BootstrapFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "account_status"]


class UserUpdateForm(BootstrapModelForm):
    new_password = forms.CharField(
        required=False, widget=forms.PasswordInput,
        help_text="Leave blank to keep the current password.",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "account_status"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("new_password"):
            user.set_password(self.cleaned_data["new_password"])  # securely hashed
        if commit:
            user.save()
        return user


class PasswordForm(BootstrapFormMixin, PasswordChangeForm):
    pass
