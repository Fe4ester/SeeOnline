# Generated by Django 5.1.6 on 2025-02-27 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_alter_trackersetting_session_string'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='onlinestatus',
            name='updated_at',
        ),
    ]
