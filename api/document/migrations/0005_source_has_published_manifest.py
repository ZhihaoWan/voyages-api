# Generated by Django 4.2.1 on 2023-11-16 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_sourcepageconnection_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='has_published_manifest',
            field=models.BooleanField(default=False, verbose_name="Is there a published manifest on dellamonica's server?"),
        ),
    ]
