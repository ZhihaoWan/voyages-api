# Generated by Django 4.2.1 on 2024-01-16 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_sourcetype_source_zotero_url_alter_source_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='title',
            field=models.CharField(max_length=1000, verbose_name='Title'),
        ),
    ]
