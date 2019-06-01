from django_extensions.management.jobs import BaseJob


class Job(BaseJob):
    help = "Job de prueba nada más."

    def execute(self):
        # executing empty sample job
        print('VAMOS A PROBAR A MANDAR UN CORREO. PRÓXIMAMENTE')
