# Generated by Django 5.1.4 on 2024-12-10 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='files/'),
        ),
        migrations.AlterField(
            model_name='reminders',
            name='platform',
            field=models.CharField(choices=[('discord', 'Discord'), ('telegram', 'Telegram'), ('slack', 'Slack')], max_length=20),
        ),
    ]
