from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import pre_delete


def check_date_not_past(value: date):
    if value < date.today():
        raise ValidationError(
            '%(value)s is in the past',
            params={'value': value},
        )


class Skill(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    STATUS = [("draft", "Черновик"), ("open", "Открыта"), ("closed", "Closed")]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(max_length=50, validators=[MinLengthValidator(3)])
    name = models.CharField(max_length=50, null=True)
    text = models.CharField(max_length=1000)
    status = models.CharField(max_length=10, choices=STATUS, default="draft")
    created = models.DateField(auto_now_add=True, validators=[check_date_not_past])
    is_archived = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

        ordering = ['name']


def archive_models(sender, instance, **kwargs):
    Vacancy.objects.fitler(user=instance).update(is_archived=True)


pre_delete.connect(archive_models, sender=User)
