# Generated by Django 5.2.1 on 2025-07-05 12:14

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('branches', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Phone number must be exactly 10 digits.', regex='^\\d{10}$')])),
                ('address', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')], default='active', max_length=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the member')),
                ('branches', models.ManyToManyField(related_name='members', to='branches.branch')),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
                'ordering': ['-created_at'],
            },
        ),
    ]
