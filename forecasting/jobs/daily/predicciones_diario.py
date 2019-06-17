from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail
from django.core.files import File

from ... import models

from ...func_datos_prediccion import crearPrediccion


class Job(BaseJob):
    help = "Creación diaria de las predicciones necesarias de los inmuebles."

    def execute(self):
        #Método real de uso
        modelos = models.ModeloConsumo.objects.all()
        for modelo in modelos:
            print('Entramos a por los modelos a hacer predicciones, darling.')
            print('Fecha de creación:')
            print(modelo.created_at)
            print('Esa era la fecha.')
            print('A continuación te digo el fichero')
            # print(modelo.fichero_modelo_inmueble.name)
            print(modelo.fichero_modelo_inmueble)
            print('Ese es el fichero')
            # fich_modelo=modelo.fichero_modelo_inmueble
            nueva_prediccion = models.PrediccionConsumo.objects.create(modelo_consumo_origen=modelo,
                                                                       fichero_prediccion_consumo=crearPrediccion(
                                                                           modelo.fichero_modelo_inmueble))
            print('Create() hecho. Vamos a guardar todo.')
            nueva_prediccion.save()
            print('Guardado.')

            print('Ahora mando EMAILS.')
            send_mail(
                'Creacion de Prediccion',
                'Ha finalizado el proceso de creacion de sus predicciones.',
                'from@example.com',
                [modelo.inmueble_origen.user.email],
                fail_silently=False,
            )

        # #Método forzado para probar funcionamiento
        # fichero = 'modeloXXX.pkl'
        # modelos=models.ModeloConsumo.objects.all()
        # for modelo in modelos:
        #     nueva_prediccion=models.PrediccionConsumo.objects.create(modelo_consumo_origen=modelo, fichero_prediccion_consumo=crearPrediccion(fichero))
        #     print('Creado, a la fuerza.')