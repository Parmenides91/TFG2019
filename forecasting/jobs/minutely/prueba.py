from django_extensions.management.jobs import BaseJob

from django.core.mail import send_mail
import pandas as pd

from ... import models


class Job(BaseJob):
    help = "Job de prueba nada más."

    def execute(self):

        print('Cojo el histórico, baby.')
        histo = models.HistoricoMercadoRegulado.objects.filter(id=1).get()
        print('La ruta es:')
        print(histo.ruta_fichero)
        print('Lo leo')
        df = pd.read_csv(histo.ruta_fichero, index_col=0, parse_dates=True)
        print(df.info())
        print('El index es:')
        print(df.index)
        df.index.freq='H'
        print('La frecuencia del index:')
        print(df.index)
        print(df.index.freq)

        # print('Recolecto')
        # histos = models.HistoricoMercadoRegulado.objects.all()
        # print('Voy a entrar al for')
        # for histo in histos:
        #     print('Hola')
        #     print(histo.ruta_fichero)
        #     df = pd.read_csv(histo.ruta_fichero, index_col=0, parse_dates=True)
        #     print(df.info())

        # executing empty sample job
        # print('VAMOS A PROBAR A MANDAR UN CORREO. PRÓXIMAMENTE')
        # # inmueble = models.Inmueble.objects.get.all()
        # # inmueble.consumo
        # # pred = models.Prediccion.objects.get
        #
        # send_mail(
        #     'Subject here',
        #     'Here is the message.',
        #     'from@example.com',
        #     ['rbeneitez@msn.com'],
        #     fail_silently=False,
        # )
        #
        # print('HECHO, DEBERÍA')
