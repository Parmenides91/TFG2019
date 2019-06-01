from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail

from ... import models


class Job(BaseJob):
    help = "Job de prueba nada más."

    def execute(self):
        # executing empty sample job
        print('VAMOS A PROBAR A MANDAR UN CORREO. PRÓXIMAMENTE')
        inmueble = models.Inmueble.objects.get.all()
        inmueble.consumo
        pred = models.Prediccion.objects.get

        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            ['rbeneitez@msn.com'],
            fail_silently=False,
        )

        print('HECHO, DEBERÍA')
