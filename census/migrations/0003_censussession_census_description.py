# Generated by Django 3.2.25 on 2024-12-20 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0002_alter_censusquestion_question_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='censussession',
            name='census_description',
            field=models.TextField(blank=True, default='', verbose_name='Census Description'),
        ),
    ]
