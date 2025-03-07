# Generated by Django 5.1.6 on 2025-03-01 03:27

import uuid6
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid6.uuid7, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('user_type', models.CharField(choices=[('guest', 'Guest'), ('registered', 'Registered')], default='guest', max_length=10)),
            ],
        ),
    ]
