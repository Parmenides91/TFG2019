# Generated by Django 2.2.1 on 2019-05-22 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0006_auto_20190516_0359'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelopred',
            name='media',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=11),
        ),
        migrations.AddField(
            model_name='modelopred',
            name='raizECM',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=11),
        ),
    ]
