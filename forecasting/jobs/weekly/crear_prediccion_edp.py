from django_extensions.management.jobs import BaseJob

import pandas as pd

from ... import models
from ...func_mr import crearPrediccionMRunico


class Job(BaseJob):
    """
    Tarea automática encargada de crear los modelos predictivos para la tarifa EDP.
    """

    help = "Crea predicciones de EDP con su modelo."

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

                if prediccionconsumo.modelo_edp_actualizado and prediccionconsumo.prediccion_edp_actualizada:
                    # El modelo EDP y su predicción ya están actualizados.
                    print('El modelo EDP y su predicción ya están actualizados.')
                elif (prediccionconsumo.modelo_edp_actualizado and (not prediccionconsumo.prediccion_edp_actualizada)):
                    # El modelo EDP está actualizado pero no hay hecha una predicción EDP.
                    print('El modelo EDP está actualizado pero no hay hecha una predicción EDP.')
                    modelos_edp = models.ModeloEDP.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_edp in modelos_edp:
                        print('Modelo EDP - id: {}'.format(modelo_edp.id))
                        print('Modelo EDP - modelo: {}'.format(modelo_edp.ruta_modelo_edp))

                        # if modelo_edp.id == 1:
                        #     print('----> ¡No me gustas!')
                        #     modelo_edp.delete()

                        ruta_prediccion_edp = crearPrediccionMRunico(modelo_edp.ruta_modelo_edp, modelo_edp.tipo,
                                                                     rango_prediccion)
                        nueva_prediccion_edp = models.PrediccionEDP.objects.create(modelo_origen=modelo_edp,
                                                                                   ruta_prediccion=ruta_prediccion_edp)
                        nueva_prediccion_edp.save()  # creada la nueva predicción

                        # El modelo sabe que ya tiene una predicción hecha (me la puedo ahorrar porque no la comprueba desde aquí)
                        modelo_edp.prediccion_edp_actualizada = True
                        modelo_edp.save()

                        # La predicción de consumo queda con su predicción de precio correspondiente
                        prediccionconsumo.prediccion_edp_actualizada = True
                        prediccionconsumo.save()
                else:
                    # Dos situaciones posibles:
                    # 1) no modeloEDP, no predicciónEDP
                    # 2) no modeloEDP, sí predicciónEDP
                    print('Jobs: Creación Predicciones EDP: caso no soportado.')

            print('Predicción EDP de Predicción de consumo - estado: {}'.format(
                prediccionconsumo.prediccion_edp_actualizada))
