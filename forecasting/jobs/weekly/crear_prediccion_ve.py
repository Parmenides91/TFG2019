from django_extensions.management.jobs import BaseJob

import pandas as pd

from ... import models
from ...func_mr import crearPrediccionMRunico


class Job(BaseJob):
    help = "Crea predicciones de VE con su modelo."

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionconsumo in prediccionesconsumo:
                df_pc = pd.read_csv(prediccionconsumo.fichero_prediccion_consumo_string, index_col=0,
                                    parse_dates=True)
                primera_fecha_prediccion = df_pc.first_valid_index()
                ultima_fecha_prediccion = df_pc.last_valid_index()
                rango_prediccion = {'principio': primera_fecha_prediccion,
                                    'final': ultima_fecha_prediccion}

                if prediccionconsumo.modelo_ve_actualizado and prediccionconsumo.prediccion_ve_actualizada:
                    # El modelo VE y su predicción ya están actualizados.
                    print('El modelo VE y su predicción ya están actualizados.')
                elif (prediccionconsumo.modelo_ve_actualizado and (not prediccionconsumo.prediccion_ve_actualizada)):
                    # El modelo VE está actualizado pero no hay hecha una predicción VE.
                    print('El modelo VE está actualizado pero no hay hecha una predicción VE.')
                    modelos_ve = models.ModeloVE.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_ve in modelos_ve:
                        print('Modelo VE - id: {}'.format(modelo_ve.id))
                        print('Modelo VE - modelo: {}'.format(modelo_ve.ruta_modelo_ve))

                        ruta_prediccion_ve = crearPrediccionMRunico(modelo_ve.ruta_modelo_ve, modelo_ve.tipo,
                                                                     rango_prediccion)
                        nueva_prediccion_ve = models.PrediccionVE.objects.create(modelo_origen=modelo_ve,
                                                                                   ruta_prediccion=ruta_prediccion_ve)
                        nueva_prediccion_ve.save()  # creada la nueva predicción

                        # El modelo sabe que ya tiene una predicción hecha (me la puedo ahorrar porque no la comprueba desde aquí)
                        modelo_ve.prediccion_ve_actualizada = True
                        modelo_ve.save()

                        # La predicción de consumo queda con su predicción de precio correspondiente
                        prediccionconsumo.prediccion_ve_actualizada = True
                        prediccionconsumo.save()
                else:
                    # Dos situaciones posibles:
                    # 1) no modeloVE, no predicciónVE
                    # 2) no modeloVE, sí predicciónVE
                    print('Jobs: Creación Predicciones VE: caso no soportado.')

            print('Predicción VE de Predicción de consumo - estado: {}'.format(
                prediccionconsumo.prediccion_ve_actualizada))
