# Generated by Django 3.2.13 on 2022-07-10 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_user', '0004_alter_account_external_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
