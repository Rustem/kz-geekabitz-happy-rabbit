# Generated by Django 4.0.5 on 2022-06-29 00:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('activity_id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=16)),
                ('description', models.CharField(blank=True, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='RewardRule',
            fields=[
                ('reward_rule_id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('duration', models.PositiveIntegerField(help_text='Minimum duration in minutes', null=True)),
                ('reward_carrots', models.IntegerField()),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.activity')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=16)),
                ('description', models.CharField(blank=True, max_length=1024, null=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='activity.category'),
        ),
        migrations.AddField(
            model_name='activity',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]