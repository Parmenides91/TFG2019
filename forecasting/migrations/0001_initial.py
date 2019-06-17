# Generated by Django 2.2.1 on 2019-06-16 23:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Consumo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('titulo', models.CharField(max_length=255, unique=True)),
                ('fichero_consumo', models.FileField(upload_to='consumos')),
                ('coste_tarifa_PPP', models.DecimalField(decimal_places=4, default=0, max_digits=8)),
                ('coste_tarifa_EDP', models.DecimalField(decimal_places=4, default=0, max_digits=8)),
                ('coste_tarifa_VE', models.DecimalField(decimal_places=4, default=0, max_digits=8)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consumos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Inmueble',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('consumo_inmueble', models.FileField(upload_to='consumosInmuebles')),
                ('consumo_inmueble_parcial', models.FileField(blank=True, upload_to='consumosInmuebles')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inmuebles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ModeloConsumo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('fichero_modelo_inmueble', models.FilePathField(path='C:\\Users\\rbene\\PycharmProjects\\ProyectoTFG\\media\\modelos')),
                ('inmueble_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.Inmueble')),
            ],
        ),
        migrations.CreateModel(
            name='ModeloPred',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('titulo', models.CharField(max_length=255, unique=True)),
                ('fichero_modeloPred', models.FileField(blank=True, upload_to='modelos')),
                ('raizECM', models.DecimalField(decimal_places=10, default=0, max_digits=11)),
                ('media', models.DecimalField(decimal_places=10, default=0, max_digits=11)),
                ('consumo_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.Consumo')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modelosPred', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TarifaElectrica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('hora_ini_periodo_gracia', models.CharField(default='14:00', max_length=5)),
                ('hora_fin_periodo_gracia', models.CharField(default='20:00', max_length=5)),
                ('precio_periodo_gracia', models.FloatField(default=0)),
                ('precio_periodo_general', models.FloatField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tarifaselectricas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PrediccionConsumo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('fichero_prediccion_consumo', models.FileField(blank=True, upload_to='predicciones')),
                ('modelo_consumo_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.ModeloConsumo')),
            ],
        ),
        migrations.CreateModel(
            name='Prediccion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('titulo', models.CharField(max_length=255, unique=True)),
                ('fichero_prediccion', models.FileField(blank=True, upload_to='predicciones')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predicciones', to=settings.AUTH_USER_MODEL)),
                ('modelopred_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.ModeloPred')),
            ],
        ),
        migrations.CreateModel(
            name='CosteInmuebleTE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actualizado', models.BooleanField(default=True)),
                ('coste', models.FloatField()),
                ('inmueble_asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.Inmueble')),
                ('tarifalectrica_asociada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.TarifaElectrica')),
            ],
        ),
        migrations.CreateModel(
            name='CosteInmuebleMR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(default='PPD', max_length=3)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actualizado', models.BooleanField(default=True)),
                ('coste', models.FloatField()),
                ('inmueble_asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.Inmueble')),
            ],
        ),
        migrations.CreateModel(
            name='ConsumoParcial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichero_consumo_parcial', models.FileField(upload_to='consumosParciales')),
                ('inmueble_asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consumosparciales', to='forecasting.Inmueble')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
