from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView


urlpatterns = [
    path('in/', views.user_login, name='login'), # вход
    path('out/', views.user_logout, name='logout'), # выход
    path('password-reset/',
             PasswordResetView.as_view(
                template_name="login_logout/password_reset_form.html",
                email_template_name="login_logout/password_reset_email.html",
                success_url=reverse_lazy("password_reset_done")
             ),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name="login_logout/password_reset_done.html"),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
            template_name="login_logout/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete")
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="login_logout/password_reset_complete.html"),
         name='password_reset_complete'),

]