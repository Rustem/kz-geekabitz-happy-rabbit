# Generated by Django 4.0.5 on 2022-07-16 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr_user', '0002_alter_account_user_alter_userprofile_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='child',
            old_name='guardian_id',
            new_name='guardian',
        ),
    ]