# Generated by Django 4.2.1 on 2023-06-01 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_june_1_2023_johnconnor_api'),
        ('geo', '0001_june_1_2023_johnconnor_api'),
        ('voyage', '0001_june_1_2023_dellamonica_enslaversmerge'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='voyage',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='broadregion',
            name='geo_location',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='geo.location', verbose_name='Broad Region Location'),
        ),
        migrations.AddField(
            model_name='place',
            name='geo_location',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='geo.location', verbose_name='Broad Region Location'),
        ),
        migrations.AddField(
            model_name='region',
            name='geo_location',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='geo.location', verbose_name='Broad Region Location'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='arrival_at_second_place_landing_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date of arrival at second place of landing (DATARR37,36,38)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='date_departed_africa_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date vessel departed Africa (DATELEFTAFR)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='departure_last_place_of_landing_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date of departure from last place of landing (DDEPAMB,*,C)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='first_dis_of_slaves_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date of first disembarkation of slaves (DATARR33,32,34)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='imp_arrival_at_port_of_dis_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Year of arrival at port of disembarkation (YEARAM)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='imp_departed_africa_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Year departed Africa'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='imp_voyage_began_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Year voyage began'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='slave_purchase_began_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date that slave purchase began (D1SLATRB,A,C)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='third_dis_of_slaves_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date of third disembarkation of slaves (DATARR40,39,41)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='vessel_left_port_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date that vessel left last slaving port (DLSLATRB,A,C)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='voyage_began_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date that voyage began (DATEDEPB,A,C)'),
        ),
        migrations.AddField(
            model_name='voyagedates',
            name='voyage_completed_sparsedate',
            field=models.OneToOneField(help_text='Date in format: MM,DD,YYYY', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='common.sparsedate', verbose_name='Date on which slave voyage completed (DATARR44,43,45)'),
        ),
        migrations.AlterField(
            model_name='africaninfo',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='cargotype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='cargounit',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='voyage',
            name='dataset',
            field=models.IntegerField(help_text='Which dataset the voyage belongs to (e.g. Transatlantic, IntraAmerican)'),
        ),
    ]
