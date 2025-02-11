# Generated by Django 2.2.1 on 2019-06-24 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0007_auto_20190624_2231'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='infoinmueble',
            name='mes_max_consumo',
        ),
        migrations.AddField(
            model_name='infoinmueble',
            name='mes_max_consumo_fecha',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='infoinmueble',
            name='mes_max_consumo_valor',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='infoinmueble',
            name='semana_max_consumo_fecha',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='infoinmueble',
            name='semana_max_consumo_valor',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='infoinmueble',
            name='consumo_max',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='infoinmueble',
            name='consumo_max_fecha',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='infoinmueble',
            name='consumo_medio',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='infoinmueble',
            name='consumo_min',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='infoinmueble',
            name='consumo_min_fecha',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
