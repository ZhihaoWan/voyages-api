# Generated by Django 4.2.1 on 2023-11-20 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0005_source_has_published_manifest'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='is_british_library',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='BL docs have been problematic, need a quick handle for them'),
        ),
        migrations.AddField(
            model_name='page',
            name='transkribus_pageid',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='shortref',
            name='transkribus_docId',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='source',
            name='is_british_library',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='BL docs have been problematic, need a quick handle for them'),
        ),
        migrations.AddField(
            model_name='source',
            name='order_in_shortref',
            field=models.IntegerField(blank=True, null=True, verbose_name="Now that we're splitting shortrefs, sources should be ordered under them"),
        ),
        migrations.AddField(
            model_name='source',
            name='zotero_grouplibrary_name',
            field=models.CharField(default='sv-docs', max_length=255),
        ),
    ]
