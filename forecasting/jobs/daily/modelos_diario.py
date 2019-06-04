from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail
from django.core.files import File

from ... import models
# from ...models import Inmueble, ModeloConsumo

from ...func_datos_modelo import creacion_modelo, crearModelo


class Job(BaseJob):
    help = "Creación diaria automática de los modelos necesarios para el usuario."

    def execute(self):
        print('Procedo a acceder a la BBDD a por los inmuebles.')
        inmuebles = models.Inmueble.objects.all()
        for inmueble in inmuebles:
            print('Allá vamos.')
            nuevo_modelo = models.ModeloConsumo.objects.create(inmueble_origen=inmueble,
                                                               fichero_modelo_inmueble=crearModelo(
                                                                   inmueble.consumo_inmueble))
            print('Vamos a guardar.')
            nuevo_modelo.save()
            print('Guardado debería estar.')

            send_mail(
                'Creación Modelo',
                'Se ha creado el nuevo modelo.',
                'from@example.com',
                [inmueble.user.email],
                fail_silently=False,
            )

# class Job(BaseJob):
#     help = "Creación de los modelos de los consumos"
#
#     def execute(self):
#         # executing empty sample job
#         inmuebles = models.Inmueble.objects.all()
#
#         for inmueble in inmuebles:
#             for consumo in inmueble.consumo_inmueble:
#                 nuevo_modelo = models.ModeloConsumo.objects.create()
#                 nuevo_modelo.fichero_modelo_inmueble=creacion_modelo(consumo)
#                 nuevo_modelo.inmueble_origen=inmueble
#                 nuevo_modelo.save()
#
#                 send_mail(
#                     'Creación Modelo',
#                     'Se ha creado el nuevo modelo.',
#                     'from@example.com',
#                     [inmueble.user.email],
#                     fail_silently=False,
#                 )
#
#
#
