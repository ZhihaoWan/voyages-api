# Generated by Django 4.0.2 on 2022-06-01 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voyage', '0005_broadregion_geo_location_place_geo_location_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='place',
            options={'verbose_name': 'Place (Port or Location)', 'verbose_name_plural': 'Places (Ports or Locations)'},
        ),
    ]