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
    help = "Mantiene actualizado el histórico de precios del Mercado Regulado"

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            tarifasMR = models.TarifaMercadoRegulado.objects.filter(user=usuario)
            print('He pillado los históricos. Vamos a abrirlos')
            for tarifaMR in tarifasMR:
                print('Leo el histórico')
                historico = pd.read_csv(tarifaMR.fichero_precios, index_col=0, parse_dates=True)
                # ultima_fecha = historico.last_valid_index().isoformat()
                ultima_fecha = historico.last_valid_index()
                ultima_fecha += timedelta(hours=1)
                ultima_fecha = ultima_fecha.isoformat()
                hoy = datetime.datetime(int(datetime.datetime.now().__format__('%Y')), int(datetime.datetime.now().__format__('%m')), int(datetime.datetime.now().__format__('%d')), 23,0,0) # la última hora del día de hoy
                hoy = hoy.isoformat()
                print('Ultima fecha - primera fecha a pedir:')
                print(ultima_fecha)
                # print('Primera desde la que pedir')
                # print(ultima_fecha)
                print('Hoy:')
                print(hoy)

                if ultima_fecha < hoy:
                    # El histórico se puede actualizar
                    print('Se puede actualizar y actualizamos!')
                    precios_MR = precios_pvpc(ultima_fecha, hoy)

                    ristra = pd.date_range(ultima_fecha, periods=len(precios_MR), freq='H')
                    precios_MR = precios_MR.drop(precios_MR.columns[0], axis=1)
                    # precios_MR = precios_MR.drop(precios_MR.columns[0], axis=1)
                    precios_MR.index = ristra

                    frames = [historico, precios_MR]
                    df_combinado = pd.concat(frames)
                    df_combinado.index.freq = 'h'

                    # print(df_combinado.tail())
                    # print(df_combinado.index)
                    # print(df_combinado.info())

                    # historico.to_csv('GORDO.csv')
                    # precios_MR.to_csv('NAA.csv')

                    # frames = [historico, precios_MR]
                    # print('LA INFO:')
                    # print(historico.info())
                    # print('LA HEAD:')
                    # print(historico.head())
                    # print('LA TAIL:')
                    # print(historico.tail())
                    # print('EL INDEX:')
                    # print(historico.index)
                    # print('LA INDEX FREQ:')
                    # print(precios_MR.index.freq)

                    # print('LA INFO:')
                    # print(precios_MR.info())
                    # print('LA HEAD:')
                    # print(precios_MR.head())
                    # print('LA TAIL:')
                    # print(precios_MR.tail())
                    # print('EL INDEX:')
                    # print(precios_MR.index)
                    # print('LA INDEX FREQ:')
                    # print(precios_MR.index.freq)
                    # df_combinado = pd.concat(frames) # primero tengo que tratar las fechas que me vienen, que probablemente sean basura fenicia

                    # df_combinado = historico
                    #

                    # Método 1:
                    ruta_fich = settings.MEDIA_ROOT + '\\preciosMR\\'
                    ruta_fich_nom = 'histo' + id_random_generator() + '.csv'
                    ruta_fich2 = ruta_fich + ruta_fich_nom
                    nuevo_con = df_combinado.to_csv(ruta_fich2)
                    el_con = open(ruta_fich2)
                    el_file = File(el_con)
                    print('VIENE EL FILE:')
                    print(el_file)
                    tarifaMR.fichero_precios.save(ruta_fich_nom, el_file)

                    # # Método 1.1:
                    # # Lo almaceno (igual que como unificaba consumos de inmueble)
                    # ruta_fich = settings.MEDIA_ROOT + '\\preciosMR\\'
                    # print(ruta_fich)
                    # ruta_fich2 = ruta_fich + 'HistoricoMR' + id_random_generator()+ '.csv'
                    # print(ruta_fich2)
                    # df_combinado.to_csv(ruta_fich2)
                    # el_con = open(ruta_fich2)
                    # el_file = File(el_con)
                    # tarifaMR.fichero_precios.save(ruta_fich2, el_file)

                    # # Método 2:
                    # ruta_fich = settings.MEDIA_ROOT + '\\preciosMR\\' + 'HistoricoMR' + id_random_generator() + '.csv'
                    # df_combinado.to_csv(ruta_fich)  # el nuevo histórico actualizado
                    # tarifaMR.fichero_precios_string = ruta_fich
                    # tarifaMR.save()
                else:
                    # Estamos al día
                    print('Nada que actualizar.')
                    pass
