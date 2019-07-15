# Generated by Django 2.2.1 on 2019-07-12 22:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0015_auto_20190712_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='costeinmueblemr',
            name='ruta_costes',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='inmueble',
            name='coste_edp_actualizado',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inmueble',
            name='coste_tpd_actualizado',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inmueble',
            name='coste_ve_actualizado',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='CosteInmuebleVE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(default='VE', max_length=3)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('coste', models.FloatField()),
                ('ruta_costes', models.CharField(blank=True, max_length=255)),
                ('inmueble_asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.Inmueble')),
            ],
        ),
        migrations.CreateModel(
            name='CosteInmuebleTPD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(default='TPD', max_length=3)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('coste', models.FloatField()),
                ('ruta_costes', models.CharField(blank=True, max_length=255)),
                ('inmueble_asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.Inmueble')),
            ],
        ),
        migrations.CreateModel(
            name='CosteInmuebleEDP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(default='EDP', max_length=3)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('coste', models.FloatField()),
                ('ruta_costes', models.CharField(blank=True, max_length=255)),
                ('inmueble_asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.Inmueble')),
            ],
        ),
    ]
