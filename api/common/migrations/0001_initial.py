# Generated by Django 4.2.1 on 2023-10-26 17:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SavedQuery',
            fields=[
                ('id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('hash', models.CharField(db_index=True, default='', max_length=255)),
                ('query', models.TextField()),
                ('is_legacy', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SparseDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)])),
                ('month', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('year', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2000)])),
            ],
        ),
    ]
