from django_extensions.management.jobs import BaseJob

from ... import models


class Job(BaseJob):
    help = "Calcula el coste de una predicción de consumo con la predicción de precio del Mercado Regulado."

    def execute(self):
        usuarios = models.User.objects.all()
        for usuario in usuarios:
            prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            for prediccionconsumo in prediccionesconsumo:
                # prediccionesmr = prediccionconsumo.modelomercadoregulado_set
                # prediccionesmr = prediccionconsumo.modelomercadoregulado_set.all()
                prediccionesmr = prediccionconsumo.modelomercadoregulado_set.filter(prediccionconsumo_asociada=prediccionconsumo)
                for prediccionmr in prediccionesmr:
                    if not prediccionconsumo.costemr_actualizado and not prediccionmr.costemr_actualizado:
                        # Hay que calcular un nuevo coste
                        print('Hay que calcular un nuevo coste')
                        # CALCULAR UN COSTE NUEVO.
                        # TEN EN CUENTA QUE HAY 3 TIPOS DE PREDICCIONES DE PRECIOS.

                        prediccionconsumo.costemr_actualizado = True
                        prediccionconsumo.save()
                        prediccionmr.costemr_actualizado = True
                        prediccionmr.save()
                    elif prediccionconsumo.costemr_actualizado and not prediccionmr.costemr_actualizado:
                        # Hay que actualizar la predicción del Mercado Regulado
                        print('Hay que actualizar la predicción del Mercado Regulado')
                    elif not prediccionconsumo.costemr_actualizado and prediccionmr.costemr_actualizado:
                        # Hay que actualizar la predición de consumo
                        print('Hay que actualizar la predición de consumo')
                    else:
                        # El coste está actualizado
                        print('El coste está actualizado')

