# Generated by Django 4.2.1 on 2023-11-14 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0003_alter_source_short_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcepageconnection',
            name='order',
            field=models.IntegerField(blank=True, null=True, verbose_name='Document page order'),
        ),
    ]