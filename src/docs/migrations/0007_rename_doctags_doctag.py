# Generated by Django 4.0.2 on 2022-10-27 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0006_doctags_doc_pub_year_doc_title_doc_tag'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DocTags',
            new_name='DocTag',
        ),
    ]