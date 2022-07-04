# Generated by Django 3.1.14 on 2022-07-04 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_populate_flatmap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='roomno',
            field=models.IntegerField(choices=[(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'), (5, 'E')]),
        ),
    ]
