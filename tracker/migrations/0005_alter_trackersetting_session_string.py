# Generated by Django 5.1.6 on 2025-02-27 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_alter_trackersetting_session_string'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackersetting',
            name='session_string',
            field=models.TextField(blank=True, max_length=512, null=True, unique=True),
        ),
    ]
