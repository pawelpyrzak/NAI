# Generated by Django 5.1.4 on 2024-12-10 23:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_file_content_alter_file_file_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='content',
        ),
    ]
