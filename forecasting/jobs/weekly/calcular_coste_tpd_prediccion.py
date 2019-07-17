from django_extensions.management.jobs import BaseJob
from django.conf import settings
import pandas as pd

from ... import models
from ...func_mr import calcular_coste_preCons_prePrec
from ...funciones_basicas import id_random_generator


class Job(BaseJob):
    """
    Tarea automática que calcula el coste de la predicción de consumo en base a la predicción de precio de la tarifa TPD.
    """

    help = "Calcula el coste de una predicción de consumo en base a una predicción de TPD"

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionconsumo in prediccionesconsumo:
                # print('Predicción id: {}'.format(prediccionconsumo.id)) # elimina esta línea
                if prediccionconsumo.modelo_tpd_actualizado and prediccionconsumo.prediccion_tpd_actualizada and prediccionconsumo.coste_tpd_actualizado:
                    # El modelo TPD, la predicción TPD y el coste TPD están actualizados. No se requiere ninguna acción.
                    print(
                        'El modelo TPD, la predicción TPD y el coste TPD están actualizados. No se requiere ninguna acción.')
                elif (prediccionconsumo.modelo_tpd_actualizado) and (
                prediccionconsumo.prediccion_tpd_actualizada) and not (prediccionconsumo.coste_tpd_actualizado):
                    # El modelo TPD y la predicción TPD están actualizados pero no el coste TPD. Se procede a crear un coste TPD.
                    print(
                        'El modelo TPD y la predicción TPD están actualizados pero no el coste TPD. Se procede a crear un coste TPD.')

                    modelos_tpd = models.ModeloTPD.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_tpd in modelos_tpd:
                        predicciones_tpd = models.PrediccionTPD.objects.filter(modelo_origen=modelo_tpd)
                        for prediccion_tpd in predicciones_tpd:
                            df_consumo = pd.read_csv(prediccionconsumo.fichero_prediccion_consumo_string, index_col=0,
                                                     parse_dates=True)
                            df_tpd = pd.read_csv(prediccion_tpd.ruta_prediccion, index_col=0, parse_dates=True)

                            info_coste = calcular_coste_preCons_prePrec(df_consumo, df_tpd, 'TPD')

                            # El coste TPD
                            # print('El coste calculado es: {}'.format(info_coste.get('valor'))) # eliminar esta línea

                            # Los datos de ambas predicciones
                            ruta_fich = settings.MEDIA_ROOT + '\\prediccionesMERGE\\'
                            ruta_pred = ruta_fich + 'predicciones_C' + '_TPD_' + id_random_generator() + '.csv'
                            info_coste.get('datos').to_csv(ruta_pred)
                            # print('Fichero con ambas predicciones: {}'.format(ruta_pred)) # eliminar esta línea
                            nuevo_coste_tpd = models.CosteTPDPrediccion.objects.create(
                                prediccion_consumo_asociada=prediccionconsumo,
                                prediccion_mr_asociada=prediccion_tpd,
                                coste=info_coste.get('valor'),
                                ruta_predicciones=ruta_pred)
                            nuevo_coste_tpd.save()
                            prediccionconsumo.coste_tpd_actualizado = True
                            prediccionconsumo.save()
                            # print('Actualizado el coste de esta predicción: {}'.format(prediccionconsumo.coste_tpd_actualizado)) #elimina esta línea

                elif (prediccionconsumo.modelo_tpd_actualizado) and not (
                prediccionconsumo.prediccion_tpd_actualizada) and not (prediccionconsumo.coste_tpd_actualizado):
                    # El modelo TPD está actualizado pero la predicción TPD (y por ende el coste TPD) no está actualizada.
                    print(
                        'El modelo TPD está actualizado pero la predicción TPD (y por ende el coste TPD) no está actualizada.')
                elif not (prediccionconsumo.modelo_tpd_actualizado) and not (
                prediccionconsumo.prediccion_tpd_actualizada) and not (prediccionconsumo.coste_tpd_actualizado):
                    print('Ni el modelo TPD, ni la predicción TPD ni el coste están actualizados.')
                else:
                    # No soportado.
                    print('Jobs: calcular_coste_tpd_prediccion.py - condición no soportada, error.')
