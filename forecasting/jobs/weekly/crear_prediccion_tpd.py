from django_extensions.management.jobs import BaseJob

import pandas as pd

from ... import models
from ...func_mr import crearPrediccionMRunico


class Job(BaseJob):
    """
    Tarea automática encargada de crear los modelos predictivos para la tarifa TDP.
    """

    help = "Crea predicciones de TPD con su modelo."

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

                if prediccionconsumo.modelo_tpd_actualizado and prediccionconsumo.prediccion_tpd_actualizada:
                    # El modelo TPD y su predicción ya están actualizados.
                    print('El modelo TPD y su predicción ya están actualizados.')
                elif (prediccionconsumo.modelo_tpd_actualizado and (not prediccionconsumo.prediccion_tpd_actualizada)):
                    # El modelo TPD está actualizado pero no hay hecha una predicción TPD.
                    print('El modelo TPD está actualizado pero no hay hecha una predicción TPD.')
                    modelos_tpd = models.ModeloTPD.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_tpd in modelos_tpd:
                        print('Modelo TPD - id: {}'.format(modelo_tpd.id))
                        print('Modelo TPD - modelo: {}'.format(modelo_tpd.ruta_modelo_tpd))

                        # if modelo_tpd.id == 1:
                        #     print('----> ¡No me gustas!')
                        #     modelo_tpd.delete()

                        ruta_prediccion_tpd = crearPrediccionMRunico(modelo_tpd.ruta_modelo_tpd, modelo_tpd.tipo,
                                                                     rango_prediccion)
                        nueva_prediccion_tpd = models.PrediccionTPD.objects.create(modelo_origen=modelo_tpd,
                                                                                   ruta_prediccion=ruta_prediccion_tpd)
                        nueva_prediccion_tpd.save()  # creada la nueva predicción

                        # El modelo sabe que ya tiene una predicción hecha (me la puedo ahorrar porque no la comprueba desde aquí)
                        modelo_tpd.prediccion_tpd_actualizada = True
                        modelo_tpd.save()

                        # La predicción de consumo queda con su predicción de precio correspondiente
                        prediccionconsumo.prediccion_tpd_actualizada = True
                        prediccionconsumo.save()
                else:
                    # Dos situaciones posibles:
                    # 1) no modeloTPD, no predicciónTPD
                    # 2) no modeloTPD, sí predicciónTPD
                    print('Jobs: Creación Predicciones TPD: caso no soportado.')

            print('Predicción TPD de Predicción de consumo - estado: {}'.format(
                prediccionconsumo.prediccion_tpd_actualizada))
