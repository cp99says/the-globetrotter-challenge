# Generated by Django 5.1.6 on 2025-03-01 17:41

import django.db.models.deletion
import uuid6
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_alter_gamesession_user'),
        ('user', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameattempts',
            name='user_id',
            field=models.ForeignKey(default=uuid6.uuid7, editable=False, on_delete=django.db.models.deletion.CASCADE, to='user.user'),
        ),
    ]
