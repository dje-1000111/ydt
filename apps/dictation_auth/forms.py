"""Item Auth forms."""
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate

from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from apps.dictation_auth.models import User

UserModel = get_user_model()
# from EmailModelBackend import authenticate


# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser

# class CustomUserCreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = UserCreationForm.Meta.fields + ('email',)


class UserCreationForm(auth_forms.UserCreationForm):
    """User creation form class."""

    class Meta(auth_forms.UserCreationForm.Meta):
        """User creation form meta class."""

        model = get_user_model()


class SignupForm(auth_forms.UserCreationForm):
    """Inscription form."""

    email = forms.CharField(
        label=_("Email address"),
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "off",
                "class": "form-control me-2",
                "input_type": "email",
                # "placeholder": _("Email"),
                "data-email": "",
            }
        ),
    )
    username = forms.CharField(
        label=_("Username"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control me-2",
                # "placeholder": "Username",
            }
        ),
    )
    password1 = forms.CharField(
        label=_("Password"),
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control me-2",
                "input_type": "password",
                # "placeholder": "Type your password",
            }
        ),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control me-2",
                "input_type": "password",
                # "placeholder": "Retype your password",
            }
        ),
    )

    class Meta:
        """InscriptForm meta class."""

        model = get_user_model()
        fields = ("username", "email", "password1", "password2")


class LoginForm(auth_forms.AuthenticationForm):
    """Login form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.invalid_login = ""
        for field in self.fields.values():
            field.error_messages = {
                "required": _("The {fieldname} field is required.").format(
                    fieldname=field.label
                ),
                "invalid_login": _("Please enter a correct email and password."),
            }

        self.invalid_login = [field.error_messages for field in self.fields.values()][
            0
        ]["invalid_login"]

    email = forms.EmailField(
        label=_("Email"),
        max_length=200,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control me-2",
                "placeholder": _(""),
                "data-email": "",
            }
        ),
    )

    password = forms.CharField(
        label=_("Password"),
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control me-2",
                "placeholder": "",
            }
        ),
    )

    class Meta:
        """LoginForm meta class."""

        model = get_user_model()
        fields = ("email", "password")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                return cleaned_data
            else:
                raise forms.ValidationError(self.invalid_login)


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    email = forms.EmailField(
        label="email",
        widget=forms.EmailInput(
            attrs={"class": "form-control me-2", "type": "email", "name": "email"}
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control me-2", "autocomplete": "new-password"}
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control me-2", "autocomplete": "new-password"}
        ),
    )


class UpdateProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = forms.CharField(
        label=_("Username"),
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control me-2 w-un-250",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username"]
        # exclude = (
        #     "username",
        #     "password",
        #     "last_login",
        #     "is_superuser",
        #     "is_staff",
        #     "is_active",
        #     "date_joined",
        #     "email_confirmed",
        #     "groups",
        #     "user_permissions",
        #     "email",
        # )


class CustomPasswordChangeForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control me-2 w-un-250",
                "autocomplete": "current-password",
                "autofocus": True,
            }
        ),
    )

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control me-2 w-un-250",
                "autocomplete": "new-password",
            }
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control me-2 w-un-250",
                "autocomplete": "new-password",
            }
        ),
    )
