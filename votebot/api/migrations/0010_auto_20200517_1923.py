# Generated by Django 3.0.3 on 2020-05-17 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20200517_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='software_running',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='session',
            name='send_voter_stats',
            field=models.BooleanField(),
        ),
    ]