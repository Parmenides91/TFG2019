from django_extensions.management.jobs import BaseJob
from datetime import timedelta

import pandas as pd

from forecasting import models
from forecasting.func_mr import crearModelosMRunicos

# Cuántas semanas atrás se han de tener en cuenta a la hora de calcular el modelo
SEMANAS_ATRAS = 5


class Job(BaseJob):
    """
    Tarea automática que se encarga de crear los modelos predictivos necesarios para la tarifa TPD del mercado regulado.
    """

    help = "Crea un modelo para la tarifa VE del mercado regulado."

    def execute(self):
        # Método 2:
        usuarios = models.User.objects.all()

        for usuario in usuarios:
            prediccionesConsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionConsumo in prediccionesConsumo:
                print('Predicción Id: {}'.format(prediccionConsumo.id))
                print('ModeloTPD de la Predicción (antes): {}'.format(prediccionConsumo.modelo_tpd_actualizado))
                # TPD
                if prediccionConsumo.modelo_tpd_actualizado:
                    # El modelo TPD está actualizado.
                    print('El modelo TPD ya está actualizado.')
                else:
                    # El modelo TPD no está actualizado. Es necesario crear uno
                    print('El modelo TPD no está actualizado. Es necesario crear uno.')
                    df_pc = pd.read_csv(prediccionConsumo.fichero_prediccion_consumo_string, index_col=0,
                                        parse_dates=True)
                    primera_fecha_prediccion = df_pc.first_valid_index()
                    ultima_fecha_prediccion = df_pc.last_valid_index()

                    # historicos = models.HistoricoMercadoRegulado.objects.all()
                    historico=models.HistoricoMercadoRegulado.objects.filter(id=1).get()

                    df_mr = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
                    df_mr.index.freq = 'h'

                    primera_fecha_historico = df_mr.first_valid_index()
                    ultima_fecha_historico = df_mr.last_valid_index()

                    ultima_fecha_modelo = primera_fecha_prediccion - timedelta(hours=1)
                    primera_fecha_modelo = primera_fecha_prediccion - timedelta(weeks=SEMANAS_ATRAS)

                    if (primera_fecha_modelo > primera_fecha_historico) and (primera_fecha_modelo < ultima_fecha_historico) and (ultima_fecha_modelo > primera_fecha_historico) and (ultima_fecha_modelo < ultima_fecha_historico):
                        # La fecha solicitada está en el histórico.
                        print('La fecha solicitada está en el histórico.')

                        df_mr = df_mr.loc[primera_fecha_modelo: ultima_fecha_modelo]

                        ruta_modeloTPD_creado = crearModelosMRunicos(df_mr, 'TPD')
                        nuevo_modeloTPD = models.ModeloTPD.objects.create(prediccionconsumo_asociada=prediccionConsumo,
                                                                          ruta_modelo_tpd=ruta_modeloTPD_creado,
                                                                          )
                        nuevo_modeloTPD.save()
                        prediccionConsumo.modelo_tpd_actualizado = True
                        prediccionConsumo.save()
                    else:
                        # La fecha solicitada no está en el histórico. se ha de actualizar el gistórico
                        print('La fecha solicitada no está en el histórico. Se ha de actualizar el histórico.')

                print('ModeloTPD de la Predicción (después): {}'.format(prediccionConsumo.modelo_tpd_actualizado))





        # # Método 1:
        # usuarios = models.User.objects.all()
        #
        # for usuario in usuarios:
        #     prediccionesConsumo = models.PrediccionConsumo.objects.filter(user=usuario)
        #     for prediccionConsumo in prediccionesConsumo:
        #         print('Predicción Id: {}'.format(prediccionConsumo.id))
        #         # TPD
        #         if prediccionConsumo.modelo_tpd_actualizado:
        #             # El modelo TPD está actualizado.
        #             print('El modelo TPD ya está actualizado.')
        #         else:
        #             # El modelo TPD no está actualizado. Es necesario crear uno
        #             print('El modelo TPD no está actualizado. Es necesario crear uno.')
        #             df_pc = pd.read_csv(prediccionConsumo.fichero_prediccion_consumo_string, index_col=0,
        #                                 parse_dates=True)
        #             primera_fecha_prediccion = df_pc.first_valid_index()
        #             ultima_fecha_prediccion = df_pc.last_valid_index()
        #
        #             historicos = models.HistoricoMercadoRegulado.objects.all()
        #             for historico in historicos:
        #                 df_mr = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
        #                 df_mr.index.freq = 'h'
        #                 ultima_fecha_modelo = primera_fecha_prediccion - timedelta(hours=1)
        #                 primera_fecha_modelo = primera_fecha_prediccion - timedelta(weeks=SEMANAS_ATRAS)
        #                 df_mr = df_mr.loc[primera_fecha_modelo: ultima_fecha_modelo]
        #
        #                 ruta_modeloTPD_creado = crearModelosMRunicos(df_mr, 'TPD')
        #                 nuevo_modeloTPD = models.ModeloTPD.objects.create(prediccionconsumo_asociada=prediccionConsumo,
        #                                                                   ruta_modelo_tpd=ruta_modeloTPD_creado,
        #                                                                   )
        #                 nuevo_modeloTPD.save()
        #                 prediccionConsumo.modelo_tpd_actualizado = True
        #                 prediccionConsumo.save()
        #
        #                 break # sólo el primer histórico
        #
        #             prediccionConsumo.save()
        #         prediccionConsumo.save()
        #     prediccionConsumo.save()