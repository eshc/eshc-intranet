# Generated by Django 3.2.25 on 2024-12-03 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apply', '0007_alter_applicationquestion_question_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationquestion',
            name='question_text',
            field=models.CharField(max_length=5000, verbose_name='Question text'),
        ),
    ]