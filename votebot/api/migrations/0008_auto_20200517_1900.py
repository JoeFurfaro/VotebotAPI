# Generated by Django 3.0.3 on 2020-05-17 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_server_software_running'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='host',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Host'),
        ),
    ]