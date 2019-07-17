from django_extensions.management.jobs import BaseJob
import datetime
import pandas as pd

from ... import models
from ...func_inmueble import coste_tarifas_usuario


class Job(BaseJob):
    """
    Tarea automática que se encarga del cálculo de un coste para una predicción de consumo en base a las tarifas eléctricas personalizadas que haya creado el usuario.
    """

    help = "Obtiene coste del consumo de un Inmueble aplicando una Tarifa Eléctrica del usuario."

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            predicciones_consumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccion_consumo in predicciones_consumo:
                if prediccion_consumo.costes_personalizadas_actualizado:
                    # Los costes de las personalizadas ya están actualizados.
                    print('Los costes de las personalizadas ya están actualizados.')
                else:
                    # Es necesario calcular los costes de las personalizadas. Procedo a ello.
                    print('Es necesario calcular los costes de las personalizadas. Procedo a ello.')
                    df = pd.read_csv(prediccion_consumo.fichero_prediccion_consumo_string, index_col=0,
                                     parse_dates=True)
                    df.index.freq = 'h'

                    if models.CostePrediccionTE.objects.exists():
                        # Existen costes antiguos. Los elimino primero.
                        print('Existen costes antiguos. Los elimino primero.')
                        costes_prediccion_te = models.CostePrediccionTE.objects.filter(
                            prediccionconsumo_asociada=prediccion_consumo)
                        for coste_prediccion_te in costes_prediccion_te:
                            print('Coste Personalizada antiguo, creado el {} va a ser eliminado'.format(coste_prediccion_te.created_at))
                            coste_prediccion_te.delete()

                    else:
                        print('No había costes antiguos.')

                    personalizadas = models.TarifaElectrica.objects.filter(user=usuario)
                    for personalizada in personalizadas:
                        coste_personalizada = coste_tarifas_usuario(df, personalizada)
                        # print(
                        #     'Nuevo coste calculado de personalizada. Coste: {} para la predicción con id: {} desde la personalizada {}'.format(
                        #         coste_personalizada, prediccion_consumo.id, personalizada.nombre))
                        nuevo_coste_personalizada_prediccion = models.CostePrediccionTE.objects.create(
                            prediccionconsumo_asociada=prediccion_consumo,
                            tarifaelectrica_asociada=personalizada,
                            coste=coste_personalizada)
                        nuevo_coste_personalizada_prediccion.save()

                    prediccion_consumo.costes_personalizadas_actualizado = True
                    prediccion_consumo.save()
                    # print('Costes Personalizadas Actualizado: {}'.format(
                    #     prediccion_consumo.costes_personalizadas_actualizado))
