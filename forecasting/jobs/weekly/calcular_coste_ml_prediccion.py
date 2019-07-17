from django_extensions.management.jobs import BaseJob
import pandas as pd

from ... import models
from ...func_tarifas_ml import calcular_costes_ml


class Job(BaseJob):
    """
    Tarea automática que se encarga del cálculo de los costes para las tarifas del mercado libre sobre los consumos que se han predicho.
    """

    help = "Calcula los costes de las tarifas que tenga el sistema sobre el Mercado Libre para las predicciones."

    def execute(self):
        # Para Predicciones de consumo
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            predicciones_consumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccion_consumo in predicciones_consumo:
                if prediccion_consumo.costes_ml_actualizado:
                    # Los costes ya están actualizados.
                    print('Los costes en el mercado libre ya están actualizados.')
                else:
                    # Es necesario calcular los costes en el mercado libre.
                    print('Es necesario calcular los costes en el mercado libre. Procedo a ello.')
                    df = pd.read_csv(prediccion_consumo.fichero_prediccion_consumo_string, index_col=0,
                                     parse_dates=True)
                    df.index.freq = 'h'

                    costes_ml_prediccion = calcular_costes_ml(df)

                    # print('PRIMERA TARIFA ML:')
                    # print('Nombre: {}'.format(costes_ml_prediccion.get('T01').get('Nombre')))
                    # print('Coste: {}'.format(costes_ml_prediccion.get('T01').get('Coste')))
                    # print('Empresa: {}'.format(costes_ml_prediccion.get('T01').get('Empresa')))
                    #
                    # print('SEGUNDA TARIFA ML:')
                    # print('Nombre: {}'.format(costes_ml_prediccion.get('T02').get('Nombre')))
                    # print('Coste: {}'.format(costes_ml_prediccion.get('T02').get('Coste')))
                    # print('Empresa: {}'.format(costes_ml_prediccion.get('T02').get('Empresa')))
                    #
                    # print('TERCERA TARIFA ML:')
                    # print('Nombre: {}'.format(costes_ml_prediccion.get('T03').get('Nombre')))
                    # print('Coste: {}'.format(costes_ml_prediccion.get('T03').get('Coste')))
                    # print('Empresa: {}'.format(costes_ml_prediccion.get('T03').get('Empresa')))

                    nueva_tarifa_ml_01 = models.CostePrediccionML.objects.create(
                        prediccion_consumo_asociada=prediccion_consumo,
                        nombre=costes_ml_prediccion.get('T01').get('Nombre'),
                        coste=costes_ml_prediccion.get('T01').get('Coste'),
                        empresa=costes_ml_prediccion.get('T01').get('Empresa'))
                    nueva_tarifa_ml_01.save()

                    nueva_tarifa_ml_02 = models.CostePrediccionML.objects.create(
                        prediccion_consumo_asociada=prediccion_consumo,
                        nombre=costes_ml_prediccion.get('T02').get('Nombre'),
                        coste=costes_ml_prediccion.get('T02').get('Coste'),
                        empresa=costes_ml_prediccion.get('T02').get('Empresa'))
                    nueva_tarifa_ml_02.save()

                    nueva_tarifa_ml_03 = models.CostePrediccionML.objects.create(
                        prediccion_consumo_asociada=prediccion_consumo,
                        nombre=costes_ml_prediccion.get('T03').get('Nombre'),
                        coste=costes_ml_prediccion.get('T03').get('Coste'),
                        empresa=costes_ml_prediccion.get('T03').get('Empresa'))
                    nueva_tarifa_ml_03.save()

                    prediccion_consumo.costes_ml_actualizado = True
                    prediccion_consumo.save()
