from django_extensions.management.jobs import BaseJob

import pandas as pd

from ... import models
from ...func_mr import crearPrediccionMR, crearPrediccionMRunico


# Te puedes cargar este fichero, lo has partido en tres. Y si te cargas este, te cargas el "crear_predicciones_mr" que es más viejo que este todavía
class Job(BaseJob):
    help = "Crea una predicción de precios de las tarifas del Mercado Regulado, cada una con su modelo."

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

                # Para TPD
                if prediccionconsumo.modelo_tpd_actulizado and prediccionconsumo.prediccion_tpd_actualizada:
                    # El modelo TPD y su predicción ya están actualizados.
                    print('El modelo TPD y su predicción ya están actualizados.')
                elif (prediccionconsumo.modelo_tpd_actulizado and (not prediccionconsumo.prediccion_tpd_actualizada)):
                    print('El modelo TPD está actualizado pero no hay hecha una predicción TPD')
                    modelos_tpd = models.ModeloTPD.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_tpd in modelos_tpd:
                        ruta_prediccion_tpd = crearPrediccionMRunico(modelo_tpd.ruta_modelo, modelo_tpd.tipo, rango_prediccion)
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
                    print('Creación Predicciones TPD: Nothing to do here.')

                # Para EDP
                if prediccionconsumo.modelo_edp_actulizado and prediccionconsumo.prediccion_edp_actualizada:
                    # El modelo EDP y su predicción ya están actualizados.
                    print('El modelo EDP y su predicción ya están actualizados.')
                elif (prediccionconsumo.modelo_edp_actulizado and (not prediccionconsumo.prediccion_edp_actualizada)):
                    print('El modelo EDP está actualizado pero no hay hecha una predicción EDP')
                    modelos_edp = models.ModeloEDP.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_edp in modelos_edp:
                        ruta_prediccion_edp = crearPrediccionMRunico(modelo_edp.ruta_modelo, modelo_edp.tipo, rango_prediccion)
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
                    print('Creación Predicciones EDP: Nothing to do here.')

                # Para VE
                if prediccionconsumo.modelo_ve_actulizado and prediccionconsumo.prediccion_ve_actualizada:
                    # El modelo VE y su predicción ya están actualizados.
                    print('El modelo VE y su predicción ya están actualizados.')
                elif (prediccionconsumo.modelo_ve_actulizado and (not prediccionconsumo.prediccion_ve_actualizada)):
                    print('El modelo VE está actualizado pero no hay hecha una predicción VE')
                    modelos_ve = models.ModeloVE.objects.filter(prediccionconsumo_asociada=prediccionconsumo)
                    for modelo_ve in modelos_ve:
                        ruta_prediccion_ve = crearPrediccionMRunico(modelo_ve.ruta_modelo, modelo_ve.tipo, rango_prediccion)
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
                    print('Creación Predicciones VE: Nothing to do here.')
