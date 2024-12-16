# Generated by Django 5.1.4 on 2024-12-14 22:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_remove_file_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('qdrant_id', models.CharField(max_length=255, unique=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='myapp.group')),
            ],
        ),
        migrations.DeleteModel(
            name='File',
        ),
    ]
