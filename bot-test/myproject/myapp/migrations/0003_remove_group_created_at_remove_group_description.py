# Generated by Django 5.1.4 on 2024-12-09 17:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_remove_group_profile_image_group_group_images'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='group',
            name='description',
        ),
    ]
