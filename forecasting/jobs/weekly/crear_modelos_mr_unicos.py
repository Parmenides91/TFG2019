from django_extensions.management.jobs import BaseJob
from datetime import timedelta

import pandas as pd

from forecasting import models
from forecasting.func_mr import crearModeloMR, crearModelosMRunicos

# Cuántas semanas atrás se han de tener en cuenta a la hora de calcular el modelo
SEMANAS_ATRAS = 5


# Has partido este fichero en tres. Lo puedes borrar.
class Job(BaseJob):
    help = "Crea un modelo para cada tarifa del Mercado Regulado para cada predicción que se tenga."

    def execute(self):
        # executing empty sample job
        usuarios = models.User.objects.all()

        for usuario in usuarios:
            prediccionesConsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionConsumo in prediccionesConsumo:
                # TPD
                if prediccionConsumo.modelo_tpd_actulizado:
                    # El modelo TPD está actualizado.
                    print('El modelo TPD ya está actualizado.')
                else:
                    # El modelo TPD no está actualizado. Es necesario crear uno
                    print('El modelo TPD no está actualizado. Es necesario crear uno.')
                    df_pc = pd.read_csv(prediccionConsumo.fichero_prediccion_consumo_string, index_col=0,
                                        parse_dates=True)
                    primera_fecha_prediccion = df_pc.first_valid_index()
                    ultima_fecha_prediccion = df_pc.last_valid_index()

                    historicos = models.HistoricoMercadoRegulado.objects.all()
                    for historico in historicos:
                        df_mr = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
                        df_mr.index.freq = 'h'
                        ultima_fecha_modelo = primera_fecha_prediccion - timedelta(hours=1)
                        primera_fecha_modelo = primera_fecha_prediccion - timedelta(weeks=SEMANAS_ATRAS)
                        df_mr = df_mr.loc[primera_fecha_modelo: ultima_fecha_modelo]

                        ruta_modeloTPD_creado = crearModelosMRunicos(df_mr, 'TPD')
                        nuevo_modeloTPD = models.ModeloTPD.objects.create(prediccionconsumo_asociada=prediccionConsumo,
                                                                          ruta_modelo_tpd=ruta_modeloTPD_creado,
                                                                          )
                        nuevo_modeloTPD.save()
                        prediccionConsumo.modelo_tpd_actualizado = True
                        prediccionConsumo.save()

                        break # sólo el primer histórico

                # EDP
                if prediccionConsumo.modelo_edp_actulizado:
                    # El modelo EDP ya está actualizado.
                    print('El modelo EDP ya está actualizado.')
                else:
                    # El modelo EDP no está actualizado. Es necesario crear uno
                    print('El modelo EDP no está actualizado. Es necesario crear uno.')
                    df_pc = pd.read_csv(prediccionConsumo.fichero_prediccion_consumo_string, index_col=0,
                                                parse_dates=True)
                    primera_fecha_prediccion = df_pc.first_valid_index()
                    ultima_fecha_prediccion = df_pc.last_valid_index()

                    historicos = models.HistoricoMercadoRegulado.objects.all()
                    for historico in historicos:
                        df_mr = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
                        df_mr.index.freq = 'h'
                        ultima_fecha_modelo = primera_fecha_prediccion - timedelta(hours=1)
                        primera_fecha_modelo = primera_fecha_prediccion - timedelta(weeks=SEMANAS_ATRAS)
                        df_mr = df_mr.loc[primera_fecha_modelo: ultima_fecha_modelo]

                        ruta_modeloEDP_creado = crearModelosMRunicos(df_mr, 'EDP')
                        nuevo_modeloEDP = models.ModeloTPD.objects.create(
                                    prediccionconsumo_asociada=prediccionConsumo,
                                    ruta_modelo_tpd=ruta_modeloEDP_creado,
                                    )
                        nuevo_modeloEDP.save()
                        prediccionConsumo.modelo_edp_actualizado = True
                        prediccionConsumo.save()

                        break  # sólo el primer histórico

                # VE
                if prediccionConsumo.modelo_ve_actulizado:
                    # El modelo VE ya está actualizado.
                    print('El modelo VE ya está actualizado.')
                else:
                    # El modelo VE no está actualizado. Es necesario crear uno
                    print('El modelo VE no está actualizado. Es necesario crear uno.')
                    df_pc = pd.read_csv(prediccionConsumo.fichero_prediccion_consumo_string, index_col=0,
                                                parse_dates=True)
                    primera_fecha_prediccion = df_pc.first_valid_index()
                    ultima_fecha_prediccion = df_pc.last_valid_index()

                    historicos = models.HistoricoMercadoRegulado.objects.all()
                    for historico in historicos:
                        df_mr = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
                        df_mr.index.freq = 'h'
                        ultima_fecha_modelo = primera_fecha_prediccion - timedelta(hours=1)
                        primera_fecha_modelo = primera_fecha_prediccion - timedelta(weeks=SEMANAS_ATRAS)
                        df_mr = df_mr.loc[primera_fecha_modelo: ultima_fecha_modelo]

                        ruta_modeloVE_creado = crearModelosMRunicos(df_mr, 'VE')
                        nuevo_modeloVE = models.ModeloVE.objects.create(
                                    prediccionconsumo_asociada=prediccionConsumo,
                                    ruta_modelo_tpd=ruta_modeloVE_creado,
                                    )
                        nuevo_modeloVE.save()
                        prediccionConsumo.modelo_ve_actualizado = True
                        prediccionConsumo.save()

                        break  # sólo el primer histórico

                    prediccionConsumo.save()
                prediccionConsumo.save()
            prediccionConsumo.save()