from django_extensions.management.jobs import BaseJob
import datetime
import pandas as pd

from ... import models
from ...func_inmueble import coste_tarifas_usuario, coste_tarifas_MR
from ...plots import precios_pvpc
from ...func_analisis_consumo import calcular_coste_tarifa_MR


class Job(BaseJob):
    help = "Obtiene coste del consumo de un Inmueble aplicando los precios del Mercado Regulado."

    def execute(self):
        usuarios = models.User.objects.all()
        print('Tengo los Usuarios')
        for usuario in usuarios:
            inmuebles = models.Inmueble.objects.filter(user=usuario)
            print('Tengo los Inmuebles del usuario.')
            for inmueble in inmuebles:
                if inmueble.actualizar_costes_MR:
                    #Hay que calcular costes

                    #pobre manera de gestionar
                    costesactuales = models.CosteInmuebleMR.objects.filter(inmueble_asociado=inmueble)
                    for costeactual in costesactuales:
                        costeactual.delete()
                    #fin de la pobre manera

                    print('Hay que calcular tarifas')
                    df = pd.read_csv(inmueble.consumo_inmueble, index_col=['Fecha'], parse_dates=True)
                    df.index.freq = 'H'
                    ini_inm=df.first_valid_index()
                    fin_inm= df.last_valid_index()
                    print('Compruebo si el usuario tiene subido algún histórico.')
                    tarifasMR = models.TarifaMercadoRegulado.objects.filter(user=usuario)
                    exito_historico = False
                    for tarifaMR in tarifasMR:
                        print('Estoy en un histórico, vamos a leerlo.')
                        df_p = pd.read_csv(tarifaMR.fichero_precios, index_col=0, parse_dates=True)
                        ini_mr=df_p.first_valid_index()
                        fin_mr=df_p.last_valid_index()
                        print(ini_inm)
                        print(fin_inm)
                        print(ini_mr)
                        print(fin_mr)
                        print(ini_inm >= ini_mr)
                        print(ini_inm <= fin_mr)
                        print(fin_inm >= ini_mr)
                        print(fin_inm <= fin_mr)
                        if (ini_inm >= ini_mr and ini_inm <= fin_mr) and (fin_inm >= ini_mr and fin_inm <= fin_mr):
                            #las fechas del consumo están dentro de las fechas de mi histórico
                            print('En este histórico tengo las fechas que necesito')
                            # SACA ESTE CÓDIGO DE AQUÍ Y PONLO EN UNA FUNCIÓN EN func_mr.py
                            df_merge = pd.merge(df, df_p, how='inner', left_index=True, right_index=True)
                            costeTPD = 0
                            costeEDP = 0
                            costeVE = 0
                            for index, row in df_merge.iterrows():
                                costeTPD += (row['TPD']) * row['Consumo_kWh']
                                costeEDP += (row['EDP']) * row['Consumo_kWh']
                                costeVE += (row['VE']) * row['Consumo_kWh']

                            costeTPD = costeTPD / 1000
                            costeEDP = costeEDP / 1000
                            costeVE = costeVE / 1000
                            print('Procedo a crear costes, en base al histórico:')
                            print('Creando Coste de TPD')
                            nuevo_costeInmuebleMRtpd = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble,
                                                                                          tipo='TPD',
                                                                                          coste=costeTPD)
                            print('Guardando TPD.')
                            nuevo_costeInmuebleMRtpd.save()

                            print('Creando Coste de EDP')
                            nuevo_costeInmuebleMRedp = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble,
                                                                                          tipo='EDP',
                                                                                          coste=costeEDP)
                            print('Guardando EDP.')
                            nuevo_costeInmuebleMRedp.save()

                            print('Creando Coste de VE')
                            nuevo_costeInmuebleMRve = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble,
                                                                                          tipo='VE',
                                                                                          coste=costeVE)
                            print('Guardando VE.')
                            nuevo_costeInmuebleMRve.save()

                            inmueble.actualizar_costes_MR = False
                            inmueble.save()

                            exito_historico = True
                            break; #ya tengo los datos, no hace falta buscar en más históricos (de haberlos)
                        else:
                            #Las fechas del Inmueble están fuera de ÉSTE histórico. Pruebo con el siguiente, si hay
                            pass
                    if not exito_historico:
                        # Ninguno de mis históricos tenía las fechas que necesitaba. Las pido al crawler
                        print('No había históricos o no tenían las fechas que necesitaba. Se las pido al crawler.')
                        print('Primera fecha:')
                        print(ini_inm)
                        print(ini_inm.isoformat())
                        print('Segunda fecha:')
                        print(fin_inm)
                        print(fin_inm.isoformat())
                        precios_MR = precios_pvpc(ini_inm.isoformat(), fin_inm.isoformat())
                        costesTarifas = coste_tarifas_MR(df, precios_MR)
                        # coste_TPD = (calcular_coste_tarifa_MR(df, precios_MR['PPD'], 'PPD')) / 1000
                        # coste_EDP = (calcular_coste_tarifa_MR(df, precios_MR['EDP'], 'EDP')) / 1000
                        # coste_VE = (calcular_coste_tarifa_MR(df, precios_MR['VE'], 'VE')) / 1000

                        print('Procedo a crear costes, con datos del crawler:')
                        print('Creando Coste de TPD')
                        print('Este precio es:')
                        print(costesTarifas.get('TPD'))
                        nuevo_costeInmuebleMRtpd = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble,
                                                                                         tipo='TPD',
                                                                                         coste=costesTarifas.get('TPD'),
                                                                                         # coste=22.2222,
                                                                                         )
                        # nuevo_costeInmuebleMRtpd.tipo = 'TPD'
                        # nuevo_costeInmuebleMRtpd.coste = 22.22
                        print('Guardando TPD.')
                        nuevo_costeInmuebleMRtpd.save()
                        print(nuevo_costeInmuebleMRtpd.coste)

                        print('Creando Coste de EDP')
                        print('Este precio es:')
                        print(costesTarifas.get('EDP'))
                        nuevo_costeInmuebleMRedp = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble,
                                                                                         tipo='EDP',
                                                                                         coste=costesTarifas.get('EDP'),
                                                                                         # coste=33.3333,
                                                                                         )
                        # nuevo_costeInmuebleMRedp.tipo = 'EDP'
                        # nuevo_costeInmuebleMRedp.coste = 33.33
                        print('Guardando EDP.')
                        nuevo_costeInmuebleMRedp.save()

                        print('Creando Coste de VE')
                        print('Este precio es:')
                        print(costesTarifas.get('VE'))
                        nuevo_costeInmuebleMRve = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble,
                                                                                        tipo='VE',
                                                                                        coste=costesTarifas.get('VE'),
                                                                                        # coste=44.4444,
                                                                                        )
                        # nuevo_costeInmuebleMRve.tipo = 'VE'
                        # nuevo_costeInmuebleMRve.coste = 44.44
                        print('Guardando VE.')
                        nuevo_costeInmuebleMRve.save()

                        inmueble.actualizar_costes_MR = False
                        inmueble.save()
                    else:
                        # Los costes se han calculado en base al histórico. Nada que hacer aquí
                        print('Los costes se han calculado en base al histórico. Nada que hacer aquí')
                        pass

                else:
                    # No hay que calcular costes porque tod está actualizado
                    print('No hay que calcular costes porque tod está actualizado')
                    pass

        print('FIN.')