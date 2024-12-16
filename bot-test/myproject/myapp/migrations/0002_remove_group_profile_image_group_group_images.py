# Generated by Django 5.1.4 on 2024-12-09 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='profile_image',
        ),
        migrations.AddField(
            model_name='group',
            name='group_images',
            field=models.ImageField(blank=True, null=True, upload_to='group_images/'),
        ),
    ]
