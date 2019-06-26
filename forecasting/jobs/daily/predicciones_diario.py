from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail
from django.core.files import File
from django.conf import settings

from ... import models

from ...func_datos_prediccion import crearPrediccion


class Job(BaseJob):
    help = "Creación diaria de las predicciones necesarias de los inmuebles."

    def execute(self):
        #Método real de uso
        modelos = models.ModeloConsumo.objects.all()
        for modelo in modelos:
            # Método 2
            if modelo.inmueble_origen.modelo_actualizado and modelo.inmueble_origen.prediccion_actualizada:
                # Ya ha sido creada la predicción más actual posible
                print('Ya ha sido creada la predicción más actual posible')
                pass
            elif modelo.inmueble_origen.modelo_actualizado and not modelo.inmueble_origen.prediccion_actualizada:
                # El modelo está actualizado pero no hay predicción hecha con ese modelo
                print('No hay predicción con el modelo actualizado')
                fich_prediccion = crearPrediccion(modelo.fichero_modelo_inmueble)
                nueva_prediccion = models.PrediccionConsumo.objects.create(modelo_consumo_origen=modelo,
                                                                           user=modelo.user,
                                                                           fichero_prediccion_consumo=fich_prediccion,
                                                                           fichero_prediccion_consumo_string=fich_prediccion)
                # nueva_prediccion.modelomr_actualizado=False #no haría falta porque por defecto se pone a False
                nueva_prediccion.save()

                modelo.inmueble_origen.prediccion_actualizada=True
                modelo.inmueble_origen.save()

                send_mail(
                    'Creacion de Prediccion',
                    'Ha finalizado el proceso de creacion de sus predicciones.',
                    settings.DEFAULT_FROM_EMAIL,
                    [modelo.inmueble_origen.user.email],
                    fail_silently=False,
                )
            else:
                # Nothing to do here, baby.
                print('No deberías haber llegado aquí, la verdad')
                pass
