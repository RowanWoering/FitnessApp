# Generated by Django 5.0.3 on 2024-04-24 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorizeapp', '0009_bodymetric'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='fat_percentage',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='muscle_percentage',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='weight',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='length',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
