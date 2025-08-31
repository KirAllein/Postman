from django.db import models

from registration.models import User
from candidates.models import Candidate
from templates.models import Template


class Vacancy(models.Model):
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacancies",
        verbose_name="Пользователь"
    )
    candidates = models.ManyToManyField(Candidate, related_name='vacancies', blank=True)
    templates = models.ManyToManyField(Template,related_name='vacancies', blank=True)
    user_company = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return f'Вакансия: {self.title}'

