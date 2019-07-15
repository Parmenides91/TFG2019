from django_extensions.management.jobs import BaseJob
from django.conf import settings
import pandas as pd

from ... import models
from ...func_mr import calcular_coste_preCons_prePrec
from ...funciones_basicas import id_random_generator


class Job(BaseJob):
    help = "Calcula el coste de una predicción de consumo en base a una predicción de EDP"

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionconsumo in prediccionesconsumo:
                # print('Predicción id: {}'.format(prediccionconsumo.id)) # elimina esta línea
                if prediccionconsumo.modelo_edp_actualizado and prediccionconsumo.prediccion_edp_actualizada and prediccionconsumo.coste_edp_actualizado:
                    # El modelo EDP, la predicción EDP y el coste EDP están actualizados. No se requiere ninguna acción.
                    print(
                        'El modelo EDP, la predicción EDP y el coste EDP están actualizados. No se requiere ninguna acción.')
                elif (prediccionconsumo.modelo_edp_actualizado) and (
                prediccionconsumo.prediccion_edp_actualizada) and not (prediccionconsumo.coste_edp_actualizado):
                    # El modelo EDP y la predicción EDP están actualizados pero no el coste EDP. Se procede a crear un coste EDP.
                    print(
                        'El modelo EDP y la predicción EDP están actualizados pero no el coste EDP. Se procede a crear un coste EDP.')

                    modelos_edp = models.ModeloEDP.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_edp in modelos_edp:
                        predicciones_edp = models.PrediccionEDP.objects.filter(modelo_origen=modelo_edp)
                        for prediccion_edp in predicciones_edp:
                            df_consumo = pd.read_csv(prediccionconsumo.fichero_prediccion_consumo_string, index_col=0,
                                                     parse_dates=True)
                            df_edp = pd.read_csv(prediccion_edp.ruta_prediccion, index_col=0, parse_dates=True)

                            info_coste = calcular_coste_preCons_prePrec(df_consumo, df_edp, 'EDP')

                            # El coste EDP
                            # print('El coste calculado es: {}'.format(info_coste.get('valor')))  # elimina esta línea

                            # Los datos de ambas predicciones
                            ruta_fich = settings.MEDIA_ROOT + '\\prediccionesMERGE\\'
                            ruta_pred = ruta_fich + 'predicciones_C' + '_EDP_' + id_random_generator() + '.csv'
                            info_coste.get('datos').to_csv(ruta_pred)
                            # print('Fichero con ambas predicciones: {}'.format(ruta_pred))  # elimina esta línea
                            nuevo_coste_edp = models.CosteEDPPrediccion.objects.create(
                                prediccion_consumo_asociada=prediccionconsumo,
                                prediccion_mr_asociada=prediccion_edp,
                                coste=info_coste.get('valor'),
                                ruta_predicciones=ruta_pred)
                            nuevo_coste_edp.save()
                            prediccionconsumo.coste_edp_actualizado = True
                            prediccionconsumo.save()
                            # print('Actualizado el coste de esta predicción: {}'.format(prediccionconsumo.coste_edp_actualizado)) # elimina esta línea

                elif (prediccionconsumo.modelo_edp_actualizado) and not (
                prediccionconsumo.prediccion_edp_actualizada) and not (prediccionconsumo.coste_edp_actualizado):
                    # El modelo EDP está actualizado pero la predicción EDP (y por ende el coste EDP) no está actualizada.
                    print(
                        'El modelo EDP está actualizado pero la predicción EDP (y por ende el coste EDP) no está actualizada.')
                elif not (prediccionconsumo.modelo_edp_actualizado) and not (
                prediccionconsumo.prediccion_edp_actualizada) and not (prediccionconsumo.coste_edp_actualizado):
                    print('Ni el modelo EDP, ni la predicción EDP ni el coste están actualizados.')
                else:
                    # No soportado.
                    print('Jobs: calcular_coste_edp_prediccion.py - condición no soportada, error.')
