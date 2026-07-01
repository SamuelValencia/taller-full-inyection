from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import LoginForm, RecuperarPasswordForm, NuevaPasswordForm

app_name = "authentication"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(
        template_name="authentication/login.html",
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="authentication/password_reset.html",
        form_class=RecuperarPasswordForm,
        email_template_name="authentication/password_reset_email.html",
        subject_template_name="authentication/password_reset_subject.txt",
        success_url="/auth/password-reset/done/",
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="authentication/password_reset_done.html",
    ), name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="authentication/password_reset_confirm.html",
        form_class=NuevaPasswordForm,
        success_url="/auth/password-reset/complete/",
    ), name="password_reset_confirm"),
    path("password-reset/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="authentication/password_reset_complete.html",
    ), name="password_reset_complete"),
]
