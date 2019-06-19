from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail
from django.core.files import File
from django.core.files.base import ContentFile
import os

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

            # # Método 2
            # nuevo_modelo = models.ModeloConsumo.objects.create(inmueble_origen=inmueble)
            # el_mode=crearModelo(inmueble.consumo_inmueble)
            # # el_file = ContentFile(el_mode)
            # # nuevo_modelo.fichero_modelo_inmueble.save('ElModelo', el_file)
            # nuevo_modelo.fichero_modelo_inmueble.save('ElModelo', el_mode)
            # nuevo_modelo.save()
            # print('fichero_modelo_inmueble')
            # print(nuevo_modelo.fichero_modelo_inmueble)
            # print('fichero_modelo_inmueble.name')
            # print(nuevo_modelo.fichero_modelo_inmueble.name)
            # print('fichero_modelo_inmueble.file')
            # print(nuevo_modelo.fichero_modelo_inmueble.file)
            # print('fichero_modelo_inmueble')
            # print(nuevo_modelo.fichero_modelo_inmueble)

            # # Método 3
            # nuevo_modelo = models.ModeloConsumo.objects.create(inmueble_origen=inmueble)
            # ruta_modelo = crearModelo(inmueble.consumo_inmueble)
            # nuevo_modelo.fichero_modelo_inmueble = ruta_modelo
            # nuevo_modelo.save()

            # Método 4
            if not inmueble.modelo_actualizado:
                # Hay que crear un modelo porque el consumo del inmueble ha sido modificado o acaba de ser creado
                # Me cargo el viejo, si es que existe.
                previo = models.ModeloConsumo.objects.filter(inmueble_origen=inmueble)
                if previo:
                    if os.path.exists(previo.fichero_modelo_inmueble_string):
                        os.remove(previo.fichero_modelo_inmueble_string)
                    else:
                        pass
                    previo.delete()
                else:
                    pass

                # Creo un modelo nuevo
                # ruta_modelo = crearModelo(inmueble.consumo_inmueble)
                ruta_modelo = crearModelo(inmueble.consumo_inmueble_string)
                nuevo_modelo = models.ModeloConsumo.objects.create(inmueble_origen=inmueble,
                                                                   fichero_modelo_inmueble=ruta_modelo)
                nuevo_modelo.save()

                # Aviso de que el modelo ya se ha creado con los cambios que se hubieran hecho en el Inmueble
                inmueble.modelo_actualizado = True
                inmueble.save()

                # Aviso al usuario
                send_mail(
                    'Creacion Modelo',
                    'Se ha creado el nuevo modelo.',
                    'from@example.com',
                    [inmueble.user.email],
                    fail_silently=False,
                )

            else:
                # El modelo que existe es correcto y no se requieren más acciones
                print('No hace falta crear un modelo nuevo.')
                pass


            # # Aviso al usuario
            # send_mail(
            #     'Creacion Modelo',
            #     'Se ha creado el nuevo modelo.',
            #     'from@example.com',
            #     [inmueble.user.email],
            #     fail_silently=False,
            # )
