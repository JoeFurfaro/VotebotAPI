# Generated by Django 3.0.3 on 2020-05-17 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200517_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]