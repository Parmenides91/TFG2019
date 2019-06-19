from django_extensions.management.jobs import BaseJob
import pandas as pd
import datetime

from ... import models
from ...plots import precios_pvpc


class Job(BaseJob):
    help = "Mantiene actualizado el histórico de precios del Mercado Regulado"

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            tarifasMR = models.TarifaMercadoRegulado.objects.filter(user=usuario)
            for tarifaMR in tarifasMR:
                historico = pd.read_csv(tarifaMR.fichero_precios, index_col=0, parse_dates=True)
                ultima_fecha = historico.last_valid_index().isoformat()
                hoy = datetime.datetime(int(datetime.datetime.now().__format__('%Y')), int(datetime.datetime.now().__format__('%m')), int(datetime.datetime.now().__format__('%d')), 23,0,0) # la última hora del día de hoy

                if ultima_fecha < hoy:
                    # El histórico se puede actualizar
                    precios_MR = precios_pvpc(ultima_fecha, hoy)
                    pass
                else:
                    # Estamos al día
                    pass
