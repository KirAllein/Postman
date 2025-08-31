from django import forms

from registration.models import User


# Форма редактирования профиля пользователя
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'company']

