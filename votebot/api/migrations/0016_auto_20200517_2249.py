# Generated by Django 3.0.3 on 2020-05-17 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_remove_voter_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voter',
            name='secret',
            field=models.CharField(max_length=64),
        ),
    ]
