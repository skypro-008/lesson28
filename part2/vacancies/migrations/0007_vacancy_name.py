# Generated by Django 3.2.7 on 2021-09-12 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0006_auto_20210912_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
