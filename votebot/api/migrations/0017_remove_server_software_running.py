# Generated by Django 3.0.3 on 2020-05-18 01:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20200517_2249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='software_running',
        ),
    ]
