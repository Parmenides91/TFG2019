from django_extensions.management.jobs import BaseJob
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd

from ... import models
from ...func_inmueble import coste_tarifas_usuario, coste_tarifas_MR
from ...plots import precios_pvpc
from ...func_analisis_consumo import calcular_coste_tarifa_MR
from ...func_inmueble import calcular_coste_mr_inmueble
from ...funciones_basicas import id_random_generator


class Job(BaseJob):
    """
    Tarea automática que calcula el coste del consumo de un inmueble en base al precio de la tarifa EDP del mercado regulado.
    """

    help = "Calcula el coste del inmueble para la tarifa EDP del mercado regulado."

    def execute(self):
        # Intento 2:
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            inmuebles = models.Inmueble.objects.filter(user=usuario)
            for inmueble in inmuebles:
                if inmueble.coste_edp_actualizado:
                    # El coste EDP actual es el correcto. Ninguna acción que hacer.
                    print('El coste EDP actual es el correcto. Ninguna acción que hacer.')

                    # # voy a mostrarlo, a ver cómo es: # puedes borrar esto al acabar
                    # costes_edp = models.CosteInmuebleEDP.objects.all()
                    # for coste_edp in costes_edp:
                    #     print('Coste id: {}'.format(coste_edp.id))
                    #     print('Coste, inmueble origen id: {}'.format(coste_edp.inmueble_asociado_id))
                    #     print('Coste, inmueble origen nombre: {}'.format(coste_edp.inmueble_asociado.nombre))

                else:
                    # El coste EDP está desactualizado. Procedo a crear uno.
                    print('El coste EDP está desactualizado.')

                    # Leo el consumo del inmueble
                    df_inm = pd.read_csv(inmueble.consumo_inmueble_string, index_col=0, parse_dates=True)
                    df_inm.index.freq = 'H'
                    primera_fecha_inmueble = df_inm.first_valid_index()
                    ultima_fecha_inmueble = df_inm.last_valid_index()

                    # Leo el histórico de precios
                    historico = models.HistoricoMercadoRegulado.objects.filter(id=1).get()
                    df_mr = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
                    df_mr.index.freq = 'h'
                    primera_fecha_historico = df_mr.first_valid_index()
                    ultima_fecha_historico = df_mr.last_valid_index()

                    if (primera_fecha_inmueble > primera_fecha_historico) and (
                            primera_fecha_inmueble < ultima_fecha_historico) and (
                            ultima_fecha_inmueble > primera_fecha_historico) and (
                            ultima_fecha_inmueble < ultima_fecha_historico):
                        # Las fechas del inmueble están en el histórico de precios.
                        print('Las fechas del inmueble están en el histórico de precios.')
                        df_mr = df_mr[primera_fecha_inmueble:ultima_fecha_inmueble]
                        df_mr.index.freq = 'h'
                        if models.CosteInmuebleEDP.objects.exists():
                            # Existe un Coste EDP antiguo. Procedo a actualizarlo.
                            print('Existe un Coste EDP antiguo. Procedo a actualizarlo.')
                            costes_edp = models.CosteInmuebleEDP.objects.all()
                            for coste_edp in costes_edp:
                                info_coste = calcular_coste_mr_inmueble(df_inm, df_mr, 'EDP')

                                # El coste EDP
                                print(
                                    'El coste calculado es: {}'.format(info_coste.get('valor')))  # eliminar esta línea

                                # Los datos de ambas dataframes
                                ruta_fich = settings.MEDIA_ROOT + '\\CostesInmueble\\'
                                ruta_pred = ruta_fich + 'coste_C' + '_EDP_' + id_random_generator() + '.csv'
                                info_coste.get('datos').to_csv(ruta_pred)
                                print('Fichero con ambos dataframes: {}'.format(ruta_pred))  # eliminar esta línea

                                # actualización
                                coste_edp.coste = info_coste.get('valor')
                                coste_edp.ruta_costes = ruta_pred
                                coste_edp.save()
                                # Aviso al inmueble de que ahora ya sí tiene
                                inmueble.coste_edp_actualizado = True
                                inmueble.save()
                                print('Actualizado el coste de este inmueble: {}'.format(
                                    inmueble.coste_edp_actualizado))  # elimina esta línea

                        else:
                            # No hay Costes EDP antiguos. Procedo a crear uno.
                            print('No hay Costes EDP antiguos. Procedo a crear uno.')

                            info_coste = calcular_coste_mr_inmueble(df_inm, df_mr, 'EDP')

                            # El coste EDP
                            print('El coste calculado es: {}'.format(info_coste.get('valor')))  # eliminar esta línea

                            # Los datos de ambos dataframes
                            ruta_fich = settings.MEDIA_ROOT + '\\CostesInmueble\\'
                            ruta_pred = ruta_fich + 'coste_C' + '_EDP_' + id_random_generator() + '.csv'
                            info_coste.get('datos').to_csv(ruta_pred)
                            print('Fichero con ambos dataframes: {}'.format(ruta_pred))  # eliminar esta línea

                            nuevo_coste_edp = models.CosteInmuebleEDP.objects.create(inmueble_asociado=inmueble,
                                                                                     coste=info_coste.get('valor'),
                                                                                     ruta_costes=ruta_pred)
                            nuevo_coste_edp.save()
                            inmueble.coste_edp_actualizado = True
                            inmueble.save()
                            print('Actualizado el coste de este inmueble: {}'.format(
                                inmueble.coste_edp_actualizado))  # elimina esta línea
                    else:
                        # Las fechas del consumo del inmueble no están en el histórico.
                        print(
                            'Las fechas del consumo del inmueble no están en el histórico. He de pedírselas al Crawler.')

                        # # Leo el consumo del inmueble # me sobra, ya lo estoy haciendo arriba.
                        # df_inm = pd.read_csv(inmueble.consumo_inmueble_string, index_col=0, parse_dates=True)
                        # df_inm.index.freq = 'H'
                        # primera_fecha_inmueble = df_inm.first_valid_index()
                        # ultima_fecha_inmueble = df_inm.last_valid_index()

                        # print('Fechas del inmueble: {} - {}'.format(primera_fecha_inmueble.isoformat(), ultima_fecha_inmueble.isoformat()))
                        primera_fecha_inmueble += timedelta(hours=1)
                        ultima_fecha_inmueble += timedelta(hours=1)
                        # print('Fechas a solicitar al crawler: {} - {}'.format(primera_fecha_inmueble.isoformat(),
                        #                                                       ultima_fecha_inmueble.isoformat()))

                        df_mr_crawler = precios_pvpc(primera_fecha_inmueble.isoformat(),
                                                     ultima_fecha_inmueble.isoformat())
                        df_mr_crawler['Fecha'] = df_mr_crawler['Fecha'].dt.tz_localize(None)
                        df_mr_crawler.index = pd.to_datetime(df_mr_crawler['Fecha'], format='%Y%m%d %H:%M:%S')
                        df_mr_crawler.index.freq = 'h'

                        if models.CosteInmuebleEDP.objects.exists():
                            # Existe un Coste EDP antiguo. Procedo a actualizarlo.
                            print('Existe un Coste EDP antiguo. Procedo a actualizarlo.')
                            costes_edp = models.CosteInmuebleEDP.objects.all()
                            for coste_edp in costes_edp:
                                info_coste = calcular_coste_mr_inmueble(df_inm, df_mr_crawler, 'EDP')

                                # El coste EDP
                                # print(
                                #     'El coste calculado es: {}'.format(info_coste.get('valor')))  # eliminar esta línea

                                # Los datos de ambas dataframes
                                ruta_fich = settings.MEDIA_ROOT + '\\CostesInmueble\\'
                                ruta_pred = ruta_fich + 'coste_C' + '_EDP_' + id_random_generator() + '.csv'
                                info_coste.get('datos').to_csv(ruta_pred)
                                # print('Fichero con ambos dataframes: {}'.format(ruta_pred))  # eliminar esta línea

                                # actualización
                                coste_edp.coste = info_coste.get('valor')
                                coste_edp.ruta_costes = ruta_pred
                                coste_edp.save()
                                # Aviso al inmueble de que ahora ya sí tiene
                                inmueble.coste_edp_actualizado = True
                                inmueble.save()
                                # print('Actualizado el coste de este inmueble: {}'.format(
                                #     inmueble.coste_edp_actualizado))  # elimina esta línea
                        else:
                            # No hay Costes EDP antiguos. Procedo a crear uno.
                            print('No hay Costes EDP antiguos. Procedo a crear uno.')

                            info_coste = calcular_coste_mr_inmueble(df_inm, df_mr, 'EDP')

                            # El coste EDP
                            # print('El coste calculado es: {}'.format(info_coste.get('valor')))  # eliminar esta línea

                            # Los datos de ambos dataframes
                            ruta_fich = settings.MEDIA_ROOT + '\\CostesInmueble\\'
                            ruta_pred = ruta_fich + 'coste_C' + '_EDP_' + id_random_generator() + '.csv'
                            info_coste.get('datos').to_csv(ruta_pred)
                            # print('Fichero con ambos dataframes: {}'.format(ruta_pred))  # eliminar esta línea

                            nuevo_coste_edp = models.CosteInmuebleEDP.objects.create(inmueble_asociado=inmueble,
                                                                                     coste=info_coste.get('valor'),
                                                                                     ruta_costes=ruta_pred)
                            nuevo_coste_edp.save()
                            inmueble.coste_edp_actualizado = True
                            inmueble.save()
                            # print('Actualizado el coste de este inmueble: {}'.format(
                            #     inmueble.coste_edp_actualizado))  # elimina esta línea
