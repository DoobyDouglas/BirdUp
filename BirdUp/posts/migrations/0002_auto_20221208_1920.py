# Generated by Django 2.2.16 on 2022-12-08 16:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Группа, на которую вы подписаны', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_following', to='posts.Group', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
    ]
