# Generated by Django 4.0.1 on 2022-01-23 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
