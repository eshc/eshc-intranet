# Generated by Django 3.2.25 on 2024-12-15 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='censusquestion',
            name='question_options',
            field=models.TextField(blank=True, max_length=300, verbose_name='Question options for \n single and multiple choice questions \n (separated by newlines)'),
        ),
    ]
