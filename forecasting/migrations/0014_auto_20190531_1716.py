# Generated by Django 2.2.1 on 2019-05-31 15:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0013_auto_20190530_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumoparcial',
            name='inmueble_asociado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consumosparciales', to='forecasting.Inmueble'),
        ),
        migrations.AlterField(
            model_name='consumoparcial',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
