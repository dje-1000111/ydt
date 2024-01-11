"""Dictation auth views."""
from typing import Any, Dict

# from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, logout
from django.views.generic import FormView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignupForm, LoginForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin


from apps.dictation_auth.models import User
from apps.dictation_auth.forms import (
    UpdateProfileForm,
    CustomPasswordChangeForm,
)
from apps.dictation_auth.utils import account_activation_token
from config import settings


def login(request):
    """Login view."""
    if request.method == "POST":
        form = LoginForm(None, request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            auth_login(
                request, user, backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect("dictation:home")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Deactivate the user until email confirmation
            user.is_active = False
            user.save()

            # Send email confirmation
            current_site = get_current_site(request)
            subject = "Activate your account"
            message = render_to_string(
                "registration/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )

            user.email_user(subject, message)
            messages.info(
                request,
                mark_safe(
                    "An activation link has been sent to your email address.<br>\
                        Please check your inbox and click the activation link to activate your account.",
                ),
            )

            return redirect("auth:signup")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def account_activation_sent(request):
    return render(request, "auth:account_activation_sent.html")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        auth_login(
            request, user, backend="apps.dictation_auth.authenticate.EmailModelBackend"
        )
        messages.success(
            request,
            mark_safe(
                f"Welcome, {user.username}! You have successfully activated your account and logged in!"
            ),
        )
        return redirect("auth:profile")
    else:
        messages.info(
            request,
            mark_safe(
                "Activation link is invalid! Please verify your email.",
            ),
        )
        return redirect("auth:signup")


@login_required
def account_activation_complete(request):
    return render(request, "registration/account_activation_complete.html")


@login_required
def profile(request):
    return render(request, "registration/profile.html")


class ProfileView(LoginRequiredMixin, FormView):
    """Profile view."""

    template_name: str = "registration/profile.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Get context data."""
        context = super().get_context_data(**kwargs)

        return context


class UpdateProfile(SuccessMessageMixin, LoginRequiredMixin, FormView):
    initial = {}
    form_class = UpdateProfileForm
    template_name: str = "registration/profile_form.html"
    model = User
    success_message = "%(username)s was updated successfully"

    # LoginRequiredMixin
    redirect_field_name = settings.LOGIN_URL
    login_url = settings.LOGIN_URL

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            User.objects.filter(pk=self.request.user.pk).update(
                username=form.instance.username
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data)

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        initial = super().get_initial()
        initial["username"] = self.request.user.username
        return initial

    def get_success_url(self) -> str:
        """Get success url."""
        return reverse("auth:profile")


class DeleteAccount(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "registration/user_confirm_delete.html"
    success_url = reverse_lazy("dictation:home")

    # LoginRequiredMixin
    redirect_field_name = settings.LOGIN_URL
    login_url = settings.LOGIN_URL

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object.id)

        if self.object.id == self.request.user.id:
            self.object.delete()
            messages.success(
                self.request,
                mark_safe("Your account has been deleted as well as your datas."),
            )
            return redirect(self.success_url)
        else:
            messages.warning(
                self.request,
                mark_safe("Permission denied."),
            )
            return redirect("auth:delete_account", pk=request.user.pk)


def user_logout(request):
    """Log out."""
    logout(request)
    return redirect("dictation:home")


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("auth:profile")
    success_message = "Your password was changed successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data)


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("auth:login")
    success_message = mark_safe(
        "We’ve emailed you instructions for setting your password,\
 if an account exists with the email you entered. You should receive them shortly.<br>\
 If you don’t receive an email, please make sure you’ve entered the address you registered with,\
 and check your spam folder."
    )

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data)
