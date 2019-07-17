from . import models
#from .models import ConsumoParcial, Inmueble
#from forecasting.models import ConsumoParcial, Inmueble

import pandas as pd
import csv
from django.core.files import File

from django.core.mail import send_mail
from .func_datos_modelo import creacion_modelo

# Sin uso actual.
def obtener_consumos_asociados(clave_usuario, clave_inmueble):
    inmueble = models.Inmueble.objects.get(user=clave_usuario, pk=clave_inmueble)
    consumos_parciales = models.ConsumoParcial.objects.filter(inmueble_asociado_id=inmueble.id)

    # """
    # consumos_parciales.
    # inmueble.consumo_inmueble = None
    # inmueble.delete()
    # """
    # """
    # for consumo_parcial in consumos_parciales:
    #     pass
    # """

    csvData = [['Person', 'Age'], ['Peter', '22'], ['Jasmine', '21'], ['Sam', '24']]
    with open('personNN.csv', 'r+') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    # csvFile.close()

    inmuebles = models.Inmueble.objects.all()

    for inmueble in inmuebles:
        fichero=creacion_modelo(inmueble.consumo_inmueble)
        #nuevo_modelo = models.ModeloConsumo(fichero_modelo_inmueble=fichero.buffer,inmueble_origen=inmueble)
        #nuevo_modelo = models.ModeloConsumo(fichero_modelo_inmueble=File(csvFile), inmueble_origen=inmueble)
        nuevo_modelo = models.ModeloConsumo.objects.create(fichero_modelo_inmueble=File(csvFile), inmueble_origen=inmueble)
        nuevo_modelo.save()
        #for consumo in inmueble.consumo_inmueble:
            #nuevo_modelo = models.ModeloConsumo.objects.create(fichero_modelo_inmueble=creacion_modelo(consumo),inmueble_origen=inmueble)
            #  nuevo_modelo = models.ModeloConsumo(fichero_modelo_inmueble=creacion_modelo(consumo.name), inmueble_origen=inmueble)
            # nuevo_modelo.fichero_modelo_inmueble = creacion_modelo(consumo)
            # nuevo_modelo.inmueble_origen = inmueble
            # nuevo_modelo.save()
        send_mail(
            'Creación Modelo',
            'Se ha creado el nuevo modelo.',
            'from@example.com',
            [inmueble.user.email],
            fail_silently=False,
        )



    completo=inmueble.consumo_inmueble
    for consumo_parcial in consumos_parciales:
        df = pd.read_csv(consumo_parcial.fichero_consumo_parcial, delimiter=';', decimal=',')
        ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H')
        df['Fecha'] = ristra
        df = df.drop(["Hora"], axis=1)
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y %H:%M')

        consumo_parcial.delete()