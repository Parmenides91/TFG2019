from django_extensions.management.jobs import BaseJob
from datetime import timedelta

import pandas as pd

from forecasting import models
from forecasting.func_mr import crearModelosMRunicos

# Cuántas semanas atrás se han de tener en cuenta a la hora de calcular el modelo
SEMANAS_ATRAS = 5


class Job(BaseJob):
    """
    Tarea automática que se encarga de crear los modelos predictivos necesarios para la tarifa EDP del mercado regulado.
    """
    help = "Crea un modelo para la tarifa EDP del mercado regulado."

    def execute(self):
        usuarios = models.User.objects.all()

        for usuario in usuarios:
            prediccionesConsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionConsumo in prediccionesConsumo:
                print('Predicción Id: {}'.format(prediccionConsumo.id))
                print('ModeloEDP de la Predicción (antes): {}'.format(prediccionConsumo.modelo_edp_actualizado))
                # EDP
                if prediccionConsumo.modelo_edp_actualizado:
                    # El modelo EDP está actualizado.
                    print('El modelo EDP ya está actualizado.')
                else:
                    # El modelo EDP no está actualizado. Es necesario crear uno
                    print('El modelo EDP no está actualizado. Es necesario crear uno.')
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

                        ruta_modeloEDP_creado = crearModelosMRunicos(df_mr, 'EDP')
                        nuevo_modeloEDP = models.ModeloEDP.objects.create(prediccionconsumo_asociada=prediccionConsumo,
                                                                          ruta_modelo_edp=ruta_modeloEDP_creado,
                                                                          )
                        nuevo_modeloEDP.save()
                        prediccionConsumo.modelo_edp_actualizado = True
                        prediccionConsumo.save()
                    else:
                        # La fecha solicitada no está en el histórico. se ha de actualizar el gistórico
                        print('La fecha solicitada no está en el histórico. Se ha de actualizar el histórico.')

                print('ModeloEDP de la Predicción (después): {}'.format(prediccionConsumo.modelo_edp_actualizado))