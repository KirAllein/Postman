from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from .forms import UserLoginForm, UserPasswordChangeForm
from django.urls import reverse_lazy


# Вход пользователя
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'login_logout/login.html', {'form': form})


# Выход пользователя
def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('login')


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("login_logout:password_change_done")
    template_name = "login_logout/password_change_form.html"

