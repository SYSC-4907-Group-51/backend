# Generated by Django 4.0.1 on 2022-01-30 21:04

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0005_usersynchronizationstatus'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserSynchronizationStatus',
            new_name='UserDevices',
        ),
    ]
