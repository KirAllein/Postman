from django.db import models


class Template(models.Model):
    title = models.CharField(max_length=150, blank=True)
    content = models.TextField(blank=True)
    user_company = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"

    def __str__(self):
        return f'Письмо: {self.title}'
