from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"


class Vacancy(models.Model):
    STATUS = [("draft", "Черновик"), ("open", "Открыта"), ("closed", "Closed")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=50)
    text = models.CharField(max_length=1000)
    status = models.CharField(max_length=10, choices=STATUS, default="draft")
    created = models.DateField(auto_now_add=True)
    skills = models.ManyToManyField(Skill)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
