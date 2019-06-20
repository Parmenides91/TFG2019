from django_extensions.management.jobs import BaseJob

from ... import models
from ...func_mr import crearPrediccionMR

class Job(BaseJob):
    help = "Crea las predicciones de precio del Mercado Regulado."

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionconsumo in prediccionesconsumo:
                modelosMR = prediccionconsumo.modelomercadoregulado_set.all()
                for modeloMR in modelosMR:
                    # Intento 2:
                    print(prediccionconsumo.modelomr_actualizado)
                    print(modeloMR.prediccionmr_actualizada)
                    # if prediccionconsumo.modelomr_actualizado and not modeloMR.prediccionmr_actualizada:
                    if True:
                        #El modelo está actualizado pero la prediccion de precios no
                        # Ten en cuenta que hay un modelo por cada tipo de tarifa
                        # Tengo que calcular la predicción
                        print('Tengo que calcular la predicción.')
                        ruta_prediccion_mr = crearPrediccionMR(modeloMR.ruta_modelo, modeloMR.tipo)
                        nueva_prediccion_mr = models.PrediccionMercadoRegulado.objects.create(modelo_tarifamr_origen=modeloMR,
                                                                                              prediccionconsumo_asociada=prediccionconsumo,
                                                                                              tipo=modeloMR.tipo,
                                                                                              ruta_prediccion=ruta_prediccion_mr)
                        nueva_prediccion_mr.tipo=modeloMR.tipo
                        nueva_prediccion_mr.save()

                        modeloMR.prediccionmr_actualizada = True
                        modeloMR.save()
                    elif prediccionconsumo.modelomr_actualizado and modeloMR.prediccion_actualizada:
                        # La predicción que hay es la más actualizada
                        print('La predicción que hay es la más actualizada')
                        pass
                    else:
                        # No tengo nada que hacer desde aquí
                        print('Nada que hacer desde aquí')

                    # # In tento 1:
                    # if prediccionconsumo.modelomr_actualizado and not modeloMR.prediccionconsumo_actualizada:
                    #     # Tengo que calcular la predicción
                    #     print('Tengo que calcular la predicción.')
                    #     #CÓDIGO AQUÍ ! ! ! ! ! ! ! !
                    # elif prediccionconsumo.modelomr_actualizado and modeloMR.prediccion_actualizada:
                    #     # La predicción que hay es la más actualizada
                    #     print('La predicción que hay es la más actualizada')
                    #     pass
                    # else:
                    #     # No tengo nada que hacer desde aquí
                    #     print('Nada que hacer desde aquí')
