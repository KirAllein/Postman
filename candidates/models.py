from django.db import models
from django.core.validators import FileExtensionValidator



class Candidate(models.Model):
    # Статусы кандидата
    STATUS_CHOICES = [
        ('New', 'Новый'),
        ('Message sent', 'Письмо отправлено'),
        ('Response recieved', 'Ответ получен'),
        ('Contact fixe', 'Контакт закреплен'),
        ('Rejected', 'Отклонен')
    ]

    firstname = models.CharField(max_length=100, verbose_name='Имя', blank=True)
    surname = models.CharField(max_length=100, verbose_name='Фамилия', blank=True)
    patronymic = models.CharField(max_length=100, verbose_name='Отчество', blank=True)
    birthday = models.DateField(verbose_name='Дата рождения', blank=True)
    email = models.EmailField(verbose_name='E-mail', blank=True)
    tg = models.CharField(max_length=100, verbose_name='Телеграм', blank=True)
    phone = models.CharField(max_length=15, verbose_name='Номер телефона', blank=True)
    cv = models.FileField(
        upload_to='cvs/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True,
        null=True,
        verbose_name='Резюме'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    notes = models.TextField(blank=True)
    user_company = models.CharField(max_length=150)


    class Meta:
        verbose_name = 'Кандидат'
        verbose_name_plural = 'Кандидаты'

    def __str__(self):
        return f'Кандидат: {self.firstname} {self.surname} {self.patronymic}'
