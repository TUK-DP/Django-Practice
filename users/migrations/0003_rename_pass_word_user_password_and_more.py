# Generated by Django 4.2.9 on 2024-07-26 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_password_user_pass_word'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='pass_word',
            new_name='password',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='user_name',
            new_name='username',
        ),
    ]
