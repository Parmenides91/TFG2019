from django_extensions.management.jobs import BaseJob

import pandas as pd

from ... import models



class Job(BaseJob):
    """
    Tarea automática que calcula la información adicional que se muestra del Inmueble.
    """

    help = "Creación de la información adicional del Inmueble."

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            inmuebles = models.Inmueble.objects.filter(user=usuario)
            for inmueble in inmuebles:
                # if inmueble.info_inmueble_actualizada:
                if False:
                    # La información adicional sobre el Inmueble está actualizada
                    print('La información adicional sobre el Inmueble está actualizada')
                else:
                    # Hay que actualizar la información adicional del Inmueble
                    print('Hay que actualizar la información adicional del Inmueble')
                    df = pd.read_csv(inmueble.consumo_inmueble_string, index_col=0, parse_dates=True)
                    df.index.freq = 'H'
                    infosInmueble = models.InfoInmueble.objects.filter(inmueble_asociado=inmueble)
                    if infosInmueble.exists():
                        print('Ya existe una instancia, la actualizo')
                        for infoInmueble in infosInmueble: # aunque sólo debería haber uno
                            infoInmueble.consumo_max = df.max()
                            infoInmueble.consumo_max_fecha = df.idxmax()[0]
                            infoInmueble.consumo_min = df.min()
                            infoInmueble.consumo_min_fecha = df.idxmin()[0]
                            infoInmueble.consumo_medio = df.mean()
                            df_w = df.resample('W').sum()
                            infoInmueble.semana_max_consumo_valor = df_w.max()
                            infoInmueble.semana_max_consumo_fecha = df_w.idxmax()[0].date()
                            df_m = df.resample('M').sum()
                            infoInmueble.mes_max_consumo_valor = df_m.max()
                            infoInmueble.mes_max_consumo_fecha = df_m.idxmax()[0].month_name()

                            print('Guardo el InfoInmueble')
                            infoInmueble.save()
                    else:
                        print('Creo la instancia')
                        nuevo_infoInmueble = models.InfoInmueble.objects.create(inmueble_asociado=inmueble)
                        nuevo_infoInmueble.consumo_max = df.max()
                        nuevo_infoInmueble.consumo_max_fecha = df.idxmax()[0]
                        nuevo_infoInmueble.consumo_min = df.min()
                        nuevo_infoInmueble.consumo_min_fecha = df.idxmin()[0]
                        nuevo_infoInmueble.consumo_medio = df.mean()
                        df_w = df.resample('W').sum()
                        nuevo_infoInmueble.semana_max_consumo_valor = df_w.max()
                        nuevo_infoInmueble.semana_max_consumo_fecha = df_w.idxmax()[0].date()
                        df_m = df.resample('M').sum()
                        nuevo_infoInmueble.mes_max_consumo_valor = df_m.max()
                        nuevo_infoInmueble.mes_max_consumo_fecha = df_m.idxmax()[0].month_name()

                        print('Guardo el InfoInmueble')
                        nuevo_infoInmueble.save()

                    # en ambos casos hemos actualizado los datos
                    print('Guardo el Inmueble')
                    inmueble.info_inmueble_actualizada = True
                    inmueble.save()


