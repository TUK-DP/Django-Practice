# Generated by Django 4.2.9 on 2024-04-17 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='isDeleted',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
