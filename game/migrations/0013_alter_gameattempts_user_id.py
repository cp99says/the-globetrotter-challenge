# Generated by Django 5.1.6 on 2025-03-01 17:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0012_gameattempts_user_id'),
        ('user', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameattempts',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user'),
        ),
    ]
