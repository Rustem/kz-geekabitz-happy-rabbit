# Generated by Django 3.2.13 on 2022-07-17 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='external_user_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='username',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]