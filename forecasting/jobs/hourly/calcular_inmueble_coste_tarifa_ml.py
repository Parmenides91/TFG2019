from django_extensions.management.jobs import BaseJob
import pandas as pd

from ... import models
from ...func_tarifas_ml import calcular_costes_ml


class Job(BaseJob):
    help = "Calcula los costes de las tarifas del Mercado Libre que haya en el sistema."

    def execute(self):
        usuarios = models.User.objects.all()
        print('Tengo los Usuarios')
        for usuario in usuarios:
            inmuebles = models.Inmueble.objects.filter(user=usuario)
            for inmueble in inmuebles:
                if inmueble.actualizar_costes_ML:
                    # hay que actualizar
                    print('Hay que actualizar')
                    df = pd.read_csv(inmueble.consumo_inmueble_string, index_col=0, parse_dates=True)
                    df.index.freq = 'H'
                    costes_ml = calcular_costes_ml(df)

                    costes_tarifas_ml = models.CosteInmuebleML.objects.filter(inmueble_asociado=inmueble)
                    if costes_tarifas_ml.exists():
                        print('Ya existen costes. Los eliminio y creo nuevos')
                        for coste_tarifas_ml in costes_tarifas_ml:
                            coste_tarifas_ml.delete()
                    else:
                        print('Aún no hay costes creados. Los creo.')

                    nueva_tarifa_ml_01 = models.CosteInmuebleML.objects.create(inmueble_asociado=inmueble,
                                                                               nombre=costes_ml.get('T01').get(
                                                                                   'Nombre'),
                                                                               coste=costes_ml.get('T01').get('Coste'),
                                                                               empresa=costes_ml.get('T01').get(
                                                                                   'Empresa'),
                                                                               )
                    nueva_tarifa_ml_01.save()
                    print('Creado el primer coste')

                    nueva_tarifa_ml_02 = models.CosteInmuebleML.objects.create(inmueble_asociado=inmueble,
                                                                               nombre=costes_ml.get('T02').get(
                                                                                   'Nombre'),
                                                                               coste=costes_ml.get('T02').get('Coste'),
                                                                               empresa=costes_ml.get('T02').get(
                                                                                   'Empresa'),
                                                                               )
                    nueva_tarifa_ml_02.save()
                    print('Creado el segundo coste')

                    nueva_tarifa_ml_03 = models.CosteInmuebleML.objects.create(inmueble_asociado=inmueble,
                                                                               nombre=costes_ml.get('T03').get(
                                                                                   'Nombre'),
                                                                               coste=costes_ml.get('T03').get('Coste'),
                                                                               empresa=costes_ml.get('T03').get(
                                                                                   'Empresa'),
                                                                               )
                    nueva_tarifa_ml_03.save()
                    print('Creado el tercer coste')

                    inmueble.actualizar_costes_ML = False
                    inmueble.save()
                    print('El Inmueble ya sabe que tienes sus costes ML actualizados')

                else:
                    # no hace falta actualizar
                    print('No hace falta actualizar')
