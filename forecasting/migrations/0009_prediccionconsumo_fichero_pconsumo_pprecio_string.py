# Generated by Django 2.2.1 on 2019-06-25 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0008_auto_20190625_0143'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediccionconsumo',
            name='fichero_pConsumo_pPrecio_string',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
