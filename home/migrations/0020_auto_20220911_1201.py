# Generated by Django 3.1.14 on 2022-09-11 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_auto_20220705_0014'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ('flat', 'roomno')},
        ),
    ]
