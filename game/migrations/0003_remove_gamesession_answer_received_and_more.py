# Generated by Django 5.1.6 on 2025-03-01 04:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_remove_game_host_gamesession_answer_received_and_more'),
        ('user', '0002_alter_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesession',
            name='answer_received',
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='question_assigned',
        ),
        migrations.AlterField(
            model_name='gamesession',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user'),
        ),
    ]
