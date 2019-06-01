from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail


class Job(BaseJob):
    help = "Job de prueba nada más."

    def execute(self):
        # executing empty sample job
        print('VAMOS A PROBAR A MANDAR UN CORREO. PRÓXIMAMENTE')

        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            ['rbeneitez@msn.com'],
            fail_silently=False,
        )

        print('HECHO, DEBERÍA')
