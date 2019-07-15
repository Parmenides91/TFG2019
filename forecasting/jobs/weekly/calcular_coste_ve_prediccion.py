from django_extensions.management.jobs import BaseJob
from django.conf import settings
import pandas as pd

from ... import models
from ...func_mr import calcular_coste_preCons_prePrec
from ...funciones_basicas import id_random_generator


class Job(BaseJob):
    help = "Calcula el coste de una predicción de consumo en base a una predicción de VE"

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionconsumo in prediccionesconsumo:
                # print('Predicción id: {}'.format(prediccionconsumo.id)) # elimina esta línea
                if prediccionconsumo.modelo_ve_actualizado and prediccionconsumo.prediccion_ve_actualizada and prediccionconsumo.coste_ve_actualizado:
                    # El modelo VE, la predicción VE y el coste VE están actualizados. No se requiere ninguna acción.
                    print(
                        'El modelo VE, la predicción VE y el coste VE están actualizados. No se requiere ninguna acción.')
                elif (prediccionconsumo.modelo_ve_actualizado) and (
                prediccionconsumo.prediccion_ve_actualizada) and not (prediccionconsumo.coste_ve_actualizado):
                    # El modelo VE y la predicción VE están actualizados pero no el coste VE. Se procede a crear un coste VE.
                    print(
                        'El modelo VE y la predicción VE están actualizados pero no el coste VE. Se procede a crear un coste VE.')

                    modelos_ve = models.ModeloVE.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_ve in modelos_ve:
                        predicciones_ve = models.PrediccionVE.objects.filter(modelo_origen=modelo_ve)
                        for prediccion_ve in predicciones_ve:
                            df_consumo = pd.read_csv(prediccionconsumo.fichero_prediccion_consumo_string, index_col=0,
                                                     parse_dates=True)
                            df_ve = pd.read_csv(prediccion_ve.ruta_prediccion, index_col=0, parse_dates=True)

                            info_coste = calcular_coste_preCons_prePrec(df_consumo, df_ve, 'VE')

                            # El coste VE
                            # print('El coste calculado es: {}'.format(info_coste.get('valor')))  # eliminar esta línea

                            # Los datos de ambas predicciones
                            ruta_fich = settings.MEDIA_ROOT + '\\prediccionesMERGE\\'
                            ruta_pred = ruta_fich + 'predicciones_C' + '_VE_' + id_random_generator() + '.csv'
                            info_coste.get('datos').to_csv(ruta_pred)
                            # print('Fichero con ambas predicciones: {}'.format(ruta_pred))  # eliminar esta línea
                            nuevo_coste_ve = models.CosteVEPrediccion.objects.create(
                                prediccion_consumo_asociada=prediccionconsumo,
                                prediccion_mr_asociada=prediccion_ve,
                                coste=info_coste.get('valor'),
                                ruta_predicciones=ruta_pred)
                            nuevo_coste_ve.save()
                            prediccionconsumo.coste_ve_actualizado = True
                            prediccionconsumo.save()
                            # print('Actualizado el coste de esta predicción: {}'.format(prediccionconsumo.coste_ve_actualizado)) # elimina esta línea

                elif (prediccionconsumo.modelo_ve_actualizado) and not (
                prediccionconsumo.prediccion_ve_actualizada) and not (prediccionconsumo.coste_ve_actualizado):
                    # El modelo VE está actualizado pero la predicción VE (y por ende el coste VE) no está actualizada.
                    print(
                        'El modelo VE está actualizado pero la predicción VE (y por ende el coste VE) no está actualizada.')
                elif not (prediccionconsumo.modelo_ve_actualizado) and not (
                prediccionconsumo.prediccion_ve_actualizada) and not (prediccionconsumo.coste_ve_actualizado):
                    print('Ni el modelo VE, ni la predicción VE ni el coste están actualizados.')
                else:
                    # No soportado.
                    print('Jobs: calcular_coste_ve_prediccion.py - condición no soportada, error.')
