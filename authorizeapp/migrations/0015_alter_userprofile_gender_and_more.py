# Generated by Django 5.0.3 on 2024-05-03 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorizeapp', '0014_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pics/fitness_img.png', max_length=1048576, null=True, upload_to='profile_pics/'),
        ),
    ]
