from django_extensions.management.jobs import BaseJob
from datetime import timedelta

import pandas as pd

from forecasting import models
from forecasting.func_mr import crearModeloMR

#Cuántas semanas atrás quieres tener en cuenta a la hora de calcular el modelo
SEMANAS_ATRAS = 5

class Job(BaseJob):
    help = "Crea los modelos del Mercado Regulado para poder hacer predicciones de precio."

    def execute(self):
        # executing empty sample job
        usuarios = models.User.objects.all()

        for usuario in usuarios:
            tarifasMR = models.TarifaMercadoRegulado.objects.filter(user=usuario)
            prediccionesConsumo = models.PrediccionConsumo.objects.filter(user=usuario)

            for prediccionConsumo in prediccionesConsumo:
                df_pc = pd.read_csv(prediccionConsumo.fichero_prediccion_consumo_string, index_col=0, parse_dates=True)
                primera_fecha_prediccion = df_pc.first_valid_index()
                ultima_fecha_prediccion = df_pc.last_valid_index()
                for tarifaMR in tarifasMR:
                    # df_mr = pd.read_csv(tarifaMR.fichero_precios_string, index_col=0, parse_dates=True)
                    df_mr = pd.read_csv(tarifaMR.fichero_precios, index_col=0, parse_dates=True)
                    ultima_fecha_modelo = primera_fecha_prediccion - timedelta(hours=1)
                    primera_fecha_modelo = primera_fecha_prediccion - timedelta(weeks=SEMANAS_ATRAS)
                    df_mr = df_mr.loc[primera_fecha_modelo : ultima_fecha_modelo]

                    ruta_modeloTPD_creado = crearModeloMR(df_mr, 'TPD')
                    nuevo_modeloTPD_mr = models.ModeloMercadoRegulado.objects.create(tarifaMR_origen=tarifaMR,
                                                                                  prediccionconsumo_asociada=prediccionConsumo,
                                                                                  ruta_modelo=ruta_modeloTPD_creado,
                                                                                  )
                    nuevo_modeloTPD_mr.tipo = 'TPD'
                    print('Procedo a guardar el ModeloTPD')
                    nuevo_modeloTPD_mr.save()

                    ruta_modeloEDP_creado = crearModeloMR(df_mr, 'EDP')
                    nuevo_modeloEDP_mr = models.ModeloMercadoRegulado.objects.create(tarifaMR_origen=tarifaMR,
                                                                                     prediccionconsumo_asociada=prediccionConsumo,
                                                                                     ruta_modelo=ruta_modeloEDP_creado,
                                                                                     )
                    nuevo_modeloEDP_mr.tipo = 'EDP'
                    print('Procedo a guardar el ModeloEDP')
                    nuevo_modeloEDP_mr.save()

                    ruta_modeloVE_creado = crearModeloMR(df_mr, 'VE')
                    nuevo_modeloVE_mr = models.ModeloMercadoRegulado.objects.create(tarifaMR_origen=tarifaMR,
                                                                                     prediccionconsumo_asociada=prediccionConsumo,
                                                                                     ruta_modelo=ruta_modeloVE_creado,
                                                                                     )
                    nuevo_modeloVE_mr.tipo = 'VE'
                    print('Procedo a guardar el ModeloVE')
                    nuevo_modeloVE_mr.save()

                    prediccionConsumo.modelomr_actualizado=True
                    prediccionConsumo.save()

        pass
