from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail
from django.core.files import File
from django.core.files.base import ContentFile

from ... import models
# from ...models import Inmueble, ModeloConsumo

from ...func_datos_modelo import creacion_modelo, crearModelo


class Job(BaseJob):
    help = "Creación diaria automática de los modelos necesarios para el usuario."

    def execute(self):
        print('Procedo a acceder a la BBDD a por los inmuebles.')
        inmuebles = models.Inmueble.objects.all()
        for inmueble in inmuebles:
            # # Método 1
            # nuevo_modelo = models.ModeloConsumo.objects.create(inmueble_origen=inmueble,
            #                                                    fichero_modelo_inmueble=crearModelo(
            #                                                        inmueble.consumo_inmueble))
            # nuevo_modelo.save()
            # el_file=File(nuevo_modelo.fichero_modelo_inmueble)
            # nuevo_modelo.fichero_modelo_inmueble.save('ElModelo', el_file)
            # print(nuevo_modelo.fichero_modelo_inmueble.name)

            # Método 2
            nuevo_modelo = models.ModeloConsumo.objects.create(inmueble_origen=inmueble)
            el_mode=crearModelo(inmueble.consumo_inmueble)
            # el_file = ContentFile(el_mode)
            # nuevo_modelo.fichero_modelo_inmueble.save('ElModelo', el_file)
            nuevo_modelo.fichero_modelo_inmueble.save('ElModelo', el_mode)
            nuevo_modelo.save()
            print('fichero_modelo_inmueble')
            print(nuevo_modelo.fichero_modelo_inmueble)
            print('fichero_modelo_inmueble.name')
            print(nuevo_modelo.fichero_modelo_inmueble.name)
            print('fichero_modelo_inmueble.file')
            print(nuevo_modelo.fichero_modelo_inmueble.file)
            print('fichero_modelo_inmueble')
            print(nuevo_modelo.fichero_modelo_inmueble)

            send_mail(
                'Creacion Modelo',
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
