from django_extensions.management.jobs import BaseJob
import datetime
import pandas as pd

from ... import models
from ...func_inmueble import coste_tarifas_usuario


class Job(BaseJob):
    help = "Obtiene coste del consumo de un Inmueble aplicando una Tarifa Eléctrica del usuario."

    def execute(self):
        usuarios = models.User.objects.all()
        print('Tengo los Usuarios')
        for usuario in usuarios:
            inmuebles = models.Inmueble.objects.filter(user=usuario)
            print('Tengo los Inmuebles del Usuario')
            for inmueble in inmuebles:
                df = pd.read_csv(inmueble.consumo_inmueble, index_col=['Fecha'], parse_dates=True)
                df.index.freq = 'H'
                tarifas = models.TarifaElectrica.objects.filter(user=usuario)
                print('Tengo las Tarifas Eléctricas del usuario')
                for tarifa in tarifas:

                    #Pobre manera de manejar las cosas: me cargo lo anterior y vuelvo a calcular tod.
                    costesactuales= models.CosteInmuebleTE.objects.filter(inmueble_asociado=inmueble, tarifaelectrica_asociada=tarifa)
                    for costeactual in costesactuales:
                        costeactual.delete()
                    #Fin de la pobre manera de manejar las cosas

                    print('Procedo a crear un Coste')
                    nuevo_costeInmuebleTE = models.CosteInmuebleTE.objects.create(inmueble_asociado=inmueble,
                                                                                  tarifaelectrica_asociada=tarifa,
                                                                                  coste=coste_tarifas_usuario(
                                                                                      df,
                                                                                      tarifa))
                    nuevo_costeInmuebleTE.modified_at = datetime.datetime.now()
                    nuevo_costeInmuebleTE.actualizado = True
                    print('Debería haberse creado. Mira:')
                    print(nuevo_costeInmuebleTE)
                    nuevo_costeInmuebleTE.save()
                    print('Se ha guardado.')

        print('Fin.')

    # inmuebles = models.Inmueble.objects.all()
    # for inmueble in inmuebles:
    #     tarifaselectricas = models.TarifaElectrica.objects.all()
    #     for tarifaelectrica in tarifaselectricas:
    #         nuevo_costeInmuebleTE = models.CosteInmuebleTE.objects.create(inmueble_asociado=inmueble, tarifaelectrica_asociada=tarifaelectrica, coste=coste_tarifas_usuario(inmueble.consumo_inmueble, tarifaelectrica))
    #         # nuevo_costeInmuebleTE.coste = coste_tarifas_usuario(inmueble.consumo_inmueble, tarifaelectrica)
    #         nuevo_costeInmuebleTE.modified_at = datetime.datetime.now()
    #         nuevo_costeInmuebleTE.actualizado = True
    #         print(nuevo_costeInmuebleTE)
    #         nuevo_costeInmuebleTE.save()
    #         print('Se ha guardado.')

    # inmuebles = models.Inmueble.objects.all()
    # for inmueble in inmuebles:
    #     costesInm = inmueble.costeinmueblete_set.all()
    #     for costeInm in costesInm:
    #         if (costeInm.modified_at < inmueble.modefied_at) or (costeInm.modified_at <costeInm.tarifaelectrica_asociada.modified_at):
    #             #Se ha modificado el inmueble o la tarifa, hay que recalcular
    #             costeInm.coste = coste_tarifas_usuario(inmueble.consumo_inmueble, costeInm.tarifaelectrica_asociada)
    #             costeInm.modified_at = datetime.datetime.now()
    #             costeInm.save()
    #         else:
    #             #No ha habido cambios, no hay nadad que hacer
    #             pass
    #
    #     tarifaselectricas = models.TarifaElectrica.objects.all()
    #     for tarifaelectrica in tarifaselectricas:
    #         pass

    # tarifaselectricas = models.TarifaElectrica.objects.all()
    # for tarifaelectrica in tarifaselectricas:
    #     inmuebles = models.Inmueble.objects.all()
    #     for inmueble in inmuebles:
    #         if models.CosteInmuebleTE.objects.exists():
    #             costesinmueblete = models.CosteInmuebleTE.objects.all()
    #             for costeinmueblete in costesinmueblete:
    #                 costeinmueblete.coste = coste_tarifas_usuario(inmueble.consumo_inmueble, tarifaelectrica)
    #                 costeinmueblete.modified_at = datetime.datetime.now()
    #                 costeinmueblete.actualizado = True
    #                 costeinmueblete.save()
    #         else:
    #             nuevo_costeInmuebleTE = models.CosteInmuebleTE.objects.create(inmueble_asociado=inmueble,
    #                                                                           tarifaelectrica_asociada=tarifaelectrica)
    #             costeTE = coste_tarifas_usuario(inmueble.consumo_inmueble)
    #             nuevo_costeInmuebleTE.coste = costeTE
    #             nuevo_costeInmuebleTE.modified_at = datetime.datetime.now()
    #             nuevo_costeInmuebleTE.actualizado = True
    #             nuevo_costeInmuebleTE.save()

    # nuevo_costeInmuebleTE = models.CosteInmuebleTE.objects.create(inmueble_asociado=inmueble, tarifaelectrica_asociada=tarifaelectrica)
    # costeTE = coste_tarifas_usuario(inmueble.consumo_inmueble)
    # nuevo_costeInmuebleTE.coste = costeTE
    # nuevo_costeInmuebleTE.modified_at=datetime.datetime.now()
    # nuevo_costeInmuebleTE.actualizado = True
    # nuevo_costeInmuebleTE.save()

    #
    # if models.TarifaElectrica.objects.exists():
    #     for inmueble in inmuebles:
    #         costeTE = coste_tarifas_usuario(inmueble.consumo_inmueble)
    # else:
    #     # No hay tarifas personalizadas para las que calcular el coste
    #     pass
