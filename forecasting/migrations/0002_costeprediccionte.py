# Generated by Django 2.2.1 on 2019-06-20 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostePrediccionTE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actualizado', models.BooleanField(default=True)),
                ('coste', models.FloatField()),
                ('prediccionconsumo_asociada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.PrediccionConsumo')),
                ('tarifaelectrica_asociada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasting.TarifaElectrica')),
            ],
        ),
    ]
