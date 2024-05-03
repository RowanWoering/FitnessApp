# Generated by Django 5.0.3 on 2024-04-25 11:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorizeapp', '0010_remove_userprofile_fat_percentage_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_sessions', models.BooleanField(default=True)),
                ('show_personal_info', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='setting_view', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
