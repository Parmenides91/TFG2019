# Generated by Django 2.2.1 on 2019-07-11 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0011_auto_20190711_2102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='prediccionconsumo',
            old_name='modelo_edp_actulizado',
            new_name='modelo_edp_actualizado',
        ),
        migrations.RenameField(
            model_name='prediccionconsumo',
            old_name='modelo_tpd_actulizado',
            new_name='modelo_tpd_actualizado',
        ),
        migrations.RenameField(
            model_name='prediccionconsumo',
            old_name='modelo_ve_actulizado',
            new_name='modelo_ve_actualizado',
        ),
    ]
