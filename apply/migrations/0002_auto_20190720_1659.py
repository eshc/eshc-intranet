# Generated by Django 2.1.10 on 2019-07-20 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apply', '0001_squashed_0005_auto_20190717_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='answers',
            field=models.ManyToManyField(blank=True, through='apply.ApplicationAnswer', to='apply.ApplicationQuestion'),
        ),
    ]
