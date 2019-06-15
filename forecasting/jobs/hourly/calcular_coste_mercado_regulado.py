from django_extensions.management.jobs import BaseJob
import datetime
import pandas as pd

from ... import models
from ...func_inmueble import coste_tarifas_usuario


class Job(BaseJob):
    help = "Obtiene coste del consumo de un Inmueble según los precios del Mercado Regulado"

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            inmuebles = models.Inmueble.objects.filter(user=usuario)
            for inmueble in inmuebles:
                df_c = pd.read_csv(inmueble.consumo_inmueble, index_col='Fecha', parse_dates=True)
                # historico = models.HistoricoMercadoRegulado.objects.filter(id=1)
                historico = models.HistoricoMercadoRegulado.precios_mr
                df_p = historico[df_c.first_valid_index(): df_c.last_valid_index()]

                df_merge = pd.merge(df_c, df_p, how='inner', left_index=True, right_index=True)

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

                print('Procedo a crear costes:')
                print('Creando Coste de TPD')
                nuevo_costeInmuebleMR = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble, tipo='TPD',
                                                                              coste=costeTPD)
                print('Guardando.')
                nuevo_costeInmuebleMR.save()

                print('Creando Coste de EDP')
                nuevo_costeInmuebleMR = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble, tipo='EDP',
                                                                              coste=costeEDP)
                print('Guardando.')
                nuevo_costeInmuebleMR.save()

                print('Creando Coste de VE')
                nuevo_costeInmuebleMR = models.CosteInmuebleMR.objects.create(inmueble_asociado=inmueble, tipo='VE',
                                                                              coste=costeVE)
                print('Guardando.')
                nuevo_costeInmuebleMR.save()
