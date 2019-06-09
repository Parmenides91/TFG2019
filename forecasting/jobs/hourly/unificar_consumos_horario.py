from django_extensions.management.jobs import BaseJob
from django.core.mail import send_mail
from django.core.files import File

from ... import models
from ...funciones_basicas import limpiarCSV

import pandas as pd

"""
No he probado este Job porque creo que esa forma de sustituir el fichero no es correcta.
Debería surgir el mismo problema que cuando edito los datos del csv en el form y los guardo, que se crea otro fichero y
    no queda asociado al inmueble.
"""


class Job(BaseJob):
    help = "Agrega los consumos parciales al consumo del inmueble al que pertenecen."

    def execute(self):
        inmuebles = models.Inmueble.objects.all()

        for inmueble in inmuebles:
            parciales = models.ConsumoParcial.objects.filter(inmueble_asociado_id=inmueble.id)
            for parcial in parciales:
                df_1 = pd.read_csv(inmueble.consumo_inmueble)
                # df_1 = pd.read_csv(inmueble.consumo_inmueble, delimiter=';', decimal=',')
                # df_1 = limpiarCSV(df_1)
                df_2 = pd.read_csv(parcial.fichero_consumo_parcial, delimiter=';', decimal=',')
                df_2 = limpiarCSV(df_2)

                ini1 = df_1.first_valid_index()
                fin1 = df_1.last_valid_index()
                ini2 = df_2.first_valid_index()
                fin2 = df_2.last_valid_index()

                if (((ini1 < ini2) and (fin1 < ini2)) or ((ini2 < ini1) and (fin2 < ini1))):
                    # Ambos consumos están separados, por delante o por detrás. Aplicando pandas.concat().
                    frames = [df_1, df_2]
                    df_combinado = pd.concat(frames)
                    df_combinado = df_combinado.resample('H').interpolate(method='linear')
                    df_combinado.index.freq = 'H'
                    fichero_combinado = df_combinado.to_csv('consumoCONCATENADO.csv')
                    inmueble.consumo_inmueble=fichero_combinado
                    inmueble.save()
                elif ((fin1 > ini2) or (fin2 > ini1)):
                    # Los consumos se solapan, parcial o totalmente. Aplicando combine_first()
                    df_combinado = df_1.combine_first(df_2)
                    df_combinado.index.freq = 'H'
                    fichero_combinado = df_combinado.to_csv('consumoCONCATENADO.csv')
                    inmueble.consumo_inmueble = fichero_combinado
                    inmueble.save()
                else:
                    #Caso no considerado. Actuar por defecto. pandas.concat().
                    frames = [df_1, df_2]
                    df_combinado = pd.concat(frames)
                    df_combinado = df_combinado.resample('H').interpolate(method='linear')
                    df_combinado.index.freq = 'H'
                    fichero_combinado = df_combinado.to_csv('consumoCONCATENADO.csv')
                    inmueble.consumo_inmueble = fichero_combinado
                    inmueble.save()