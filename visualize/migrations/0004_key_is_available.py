# Generated by Django 4.0.1 on 2022-02-04 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualize', '0003_authorizationkey'),
    ]

    operations = [
        migrations.AddField(
            model_name='key',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]