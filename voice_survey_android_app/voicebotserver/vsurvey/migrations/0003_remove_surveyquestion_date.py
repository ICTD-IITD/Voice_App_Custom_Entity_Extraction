# Generated by Django 2.2.5 on 2020-11-06 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vsurvey', '0002_auto_20201106_1006'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='surveyquestion',
            name='date',
        ),
    ]