# Generated by Django 4.2.1 on 2023-08-02 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('past', '0007_alter_enslaved_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='enslavementrelation',
            name='is_from_voyages',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='enslavedinrelation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='enslavementrelation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='enslavementrelation',
            name='text_ref',
            field=models.CharField(blank=True, help_text='Source text reference', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='enslaverinrelation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterUniqueTogether(
            name='enslavedinrelation',
            unique_together={('relation', 'enslaved')},
        ),
        migrations.AlterUniqueTogether(
            name='enslaverinrelation',
            unique_together={('relation', 'enslaver_alias', 'role')},
        ),
    ]
