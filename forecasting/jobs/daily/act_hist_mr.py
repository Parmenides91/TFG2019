from django_extensions.management.jobs import BaseJob
from django.core.files import File
from django.conf import settings
import pandas as pd
import datetime
from datetime import timedelta

from ... import models
from ...plots import precios_pvpc
from ...funciones_basicas import id_random_generator



class Job(BaseJob):
    help = "Actualiza el fichero que contiene el histórico de precios del Mercado Regulado"

    def execute(self):

        historicos = models.HistoricoMercadoRegulado.objects.all()

        for historico in historicos:
            # historico.ruta_fichero=settings.MEDIA_ROOT + '\\historicoMR\\' + 'HistoricoPreciosMR' +'.csv'
            # historico.save()
            df = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
            df.index.freq='h'

            ultima_fecha = df.last_valid_index()
            ultima_fecha += timedelta(hours=1)
            ultima_fecha = ultima_fecha.isoformat()
            hoy = datetime.datetime(int(datetime.datetime.now().__format__('%Y')),
                                    int(datetime.datetime.now().__format__('%m')),
                                    int(datetime.datetime.now().__format__('%d')), 23, 0,
                                    0)  # la última hora del día de hoy
            hoy = hoy.isoformat()
            print('Última fecha / primera fecha a solicitar: {}'.format(ultima_fecha))
            print('Hoy: {}'.format(hoy))

            if ultima_fecha < hoy:
                # Hay fechas nuevas que se pueden añadir. Las obtengo mediante el crawler
                print('Hay fechas nuevas que se pueden añadir. Las obtengo mediante el crawler')
                df_nuevos = precios_pvpc(ultima_fecha, hoy)
                ristra = pd.date_range(ultima_fecha, periods=len(df_nuevos), freq='H')
                df_nuevos = df_nuevos.drop(df_nuevos.columns[0], axis=1)
                df_nuevos.index = ristra

                frames = [df, df_nuevos]
                df_combinado = pd.concat(frames)
                df_combinado.index.freq = 'h'

                ruta_fich = settings.MEDIA_ROOT + '\\historicoMR\\'
                # ruta_fich_nom = 'HistoricoPreciosMR' + id_random_generator() + '.csv'
                ruta_fich_nom = 'HistoricoPreciosMRact' +'.csv'
                ruta_fich2 = ruta_fich + ruta_fich_nom
                df_combinado.to_csv(ruta_fich2)
                historico.ruta_fichero = ruta_fich2
                historico.save()

            else:
                # No hay nuevas fechas para añadir.
                print('No hay nuevas fechas para añadir.')

            break # no más de un histórico
