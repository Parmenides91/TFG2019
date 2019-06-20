from django_extensions.management.jobs import BaseJob
import pandas as pd

from ... import models
from ...func_mr import crear_costes_mr_prediccion


class Job(BaseJob):
    help = "Calcula el coste de una predicción de consumo con la predicción de precio del Mercado Regulado."

    def execute(self):
        # Intento 2:
        usuarios = models.User.objects.all()
        print('Tengos los Usuarios')
        for usuario in usuarios:
            print('Voy a por las predicciones de consumo de cada usuario:')
            prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
            print('Tengo las predicciones de consumo')
            for prediccionconsumo in prediccionesconsumo:
                print('Voy a coger todos los modelos (debería haber 3) que hay creados para esta predicción de consumo:')
                modelosmr = prediccionconsumo.modelomercadoregulado_set.filter(prediccionconsumo_asociada=prediccionconsumo)
                print('Tengo los modelos que se han creado')
                for modelomr in modelosmr:
                    print('Vamos a coger las predicciones de precios que se han generado con cada uno de esos modelos:')
                    prediccionesmr = modelomr.prediccionmercadoregulado_set.filter(modelo_tarifamr_origen=modelomr)
                    print('Voy a entrar en cada predicción de precios hecha:')
                    for prediccionmr in prediccionesmr:
                        print('Dentro de una predicción de precios.')
                        print('El coste de precios está actualizado (visto desde la prediccion de consumo):')
                        print(prediccionconsumo.costemr_actualizado)
                        print('El coste de precios está actualizado (visto desde la prediccion de precios):')
                        print(prediccionmr.costemr_actualizado)
                        if not prediccionconsumo.costemr_actualizado and not prediccionmr.costemr_actualizado:
                            # Hay que calcular un nuevo coste
                            print('PRIMER CASO:')
                            print('Hay que calcular un nuevo coste.')
                            df_c = pd.read_csv(prediccionconsumo.fichero_prediccion_consumo_string, index_col=0, parse_dates=True)
                            df_p = pd.read_csv(prediccionmr.ruta_prediccion, index_col=0, parse_dates=True)
                            coste_mr = crear_costes_mr_prediccion(df_c, df_p, prediccionmr.tipo)

                            if prediccionmr.tipo == 'TPD':
                                print('Tengo una predicción de precios de TPD')
                                print('Calculando coste para TPD')
                                nuevo_costeMRPrediccion_tpd = models.CosteMRPrediccion.objects.create(prediccionconsumo_asociada=prediccionconsumo, prediccionmr_asociada=prediccionmr,coste=coste_mr)
                                nuevo_costeMRPrediccion_tpd.save()
                            elif prediccionmr.tipo == 'EDP':
                                print('Tengo una predicción de precios de EDP')
                                print('Calculando coste para EDP')
                                nuevo_costeMRPrediccion_edp = models.CosteMRPrediccion.objects.create(
                                    prediccionconsumo_asociada=prediccionconsumo, prediccionmr_asociada=prediccionmr,
                                    coste=coste_mr)
                                nuevo_costeMRPrediccion_edp.save()
                            else:
                                print('Tengo una predicción de precios de VE')
                                print('Calculando coste para VE')
                                nuevo_costeMRPrediccion_ve = models.CosteMRPrediccion.objects.create(
                                    prediccionconsumo_asociada=prediccionconsumo, prediccionmr_asociada=prediccionmr,
                                    coste=coste_mr)
                                nuevo_costeMRPrediccion_ve.save()
                        elif prediccionconsumo.costemr_actualizado and not prediccionmr.costemr_actualizado:
                            # Hay que actualizar la predicción del Mercado Regulado
                            print('SEGUNDO CASO:')
                            print('Hay que actualizar la predicción del Mercado Regulado')
                        elif not prediccionconsumo.costemr_actualizado and prediccionmr.costemr_actualizado:
                            # Hay que actualizar la predición de consumo
                            print('TERCER CASO:')
                            print('Hay que actualizar la predición de consumo')
                        else:
                            # El coste está actualizado
                            print('CUARTO CASO:')
                            print('El coste está actualizado')



        # # Intento 1:
        # usuarios = models.User.objects.all()
        # for usuario in usuarios:
        #     prediccionesconsumo = models.PrediccionConsumo.objects.filter(user=usuario)
        #     for prediccionconsumo in prediccionesconsumo:
        #         # prediccionesmr = prediccionconsumo.modelomercadoregulado_set
        #         # prediccionesmr = prediccionconsumo.modelomercadoregulado_set.all()
        #         prediccionesmr = prediccionconsumo.modelomercadoregulado_set.filter(prediccionconsumo_asociada=prediccionconsumo)
        #         for prediccionmr in prediccionesmr:
        #             print(prediccionconsumo.costemr_actualizado)
        #             # if not prediccionconsumo.costemr_actualizado and not prediccionmr.costemr_actualizado:
        #             if True:
        #                 # Hay que calcular un nuevo coste
        #                 print('Hay que calcular un nuevo coste')
        #                 # CALCULAR UN COSTE NUEVO.
        #                 # TEN EN CUENTA QUE HAY 3 TIPOS DE PREDICCIONES DE PRECIOS.
        #                 # Prueba 1:
        #                 df_c = pd.read_csv(prediccionconsumo.fichero_prediccion_consumo_string, index_col=0, parse_dates=True)
        #                 df_p = pd.read_csv(prediccionmr.ruta_prediccion, index_col=0, parse_dates=True)
        #                 coste_mr = crear_costes_mr_prediccion(df_c, df_p, prediccionmr.tipo)
        #
        #                 if prediccionmr.tipo == 'TPD':
        #                     nuevo_costeMRPrediccion_tpd = models.CosteMRPrediccion.objects.create(
        #                         prediccionconsumo_asociada=prediccionconsumo,
        #                         prediccionmr_asociada=prediccionmr,
        #                         coste=coste_mr)
        #                     nuevo_costeMRPrediccion_tpd.save()
        #                 elif prediccionmr.modelo_tarifamr_origen.tipo == 'EDP':
        #                     nuevo_costeMRPrediccion_EDP = models.CosteMRPrediccion.objects.create(
        #                         prediccionconsumo_asociada=prediccionconsumo,
        #                         prediccionmr_asociada=prediccionmr,
        #                         coste=coste_mr)
        #                     nuevo_costeMRPrediccion_EDP.save()
        #                 else:
        #                     nuevo_costeMRPrediccion_VE = models.CosteMRPrediccion.objects.create(
        #                         prediccionconsumo_asociada=prediccionconsumo,
        #                         prediccionmr_asociada=prediccionmr,
        #                         coste=coste_mr)
        #                     nuevo_costeMRPrediccion_VE.save()
        #
        #                 prediccionconsumo.costemr_actualizado = True
        #                 prediccionconsumo.save()
        #                 prediccionmr.costemr_actualizado = True
        #                 prediccionmr.save()
        #             elif prediccionconsumo.costemr_actualizado and not prediccionmr.costemr_actualizado:
        #                 # Hay que actualizar la predicción del Mercado Regulado
        #                 print('Hay que actualizar la predicción del Mercado Regulado')
        #             elif not prediccionconsumo.costemr_actualizado and prediccionmr.costemr_actualizado:
        #                 # Hay que actualizar la predición de consumo
        #                 print('Hay que actualizar la predición de consumo')
        #             else:
        #                 # El coste está actualizado
        #                 print('El coste está actualizado')

