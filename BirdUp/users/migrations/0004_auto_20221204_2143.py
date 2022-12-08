# Generated by Django 2.2.16 on 2022-12-04 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_profile_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='profile',
            name='about',
            field=models.TextField(blank=True, null=True, verbose_name='О себе'),
        ),
    ]