# Generated by Django 3.0.3 on 2020-05-17 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20200505_0147'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='observer_key',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='send_voter_stats',
            field=models.BooleanField(default=False),
        ),
    ]