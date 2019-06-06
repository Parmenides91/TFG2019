import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from django.core.files import File

# Load specific forecasting tools
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAXResults


def crearPrediccion(fichero):
    print('Has entrado a la función')
    print(File(fichero))
    print('Cargamos el fichero')
    loaded = SARIMAXResults.load(fichero)
    print('Ya está cargado')

    DIAS_A_PREDECIR = 7

    inicio = datetime.today().__format__('%Y-%m-%d')  # Hoy
    final = datetime.today()
    for i in range(DIAS_A_PREDECIR):
        final += timedelta(days=1)
    final = final.__format__('%Y-%m-%d')  # x DÍAS EN ADELANTE

    inicio = datetime(2018, 3, 1, 0, 0, 0)  # fuerzo un día en concreto because boobs
    final = datetime(2018, 3, 7, 0, 0, 0)  # fuerzo un día en concreto because boobs
    # print(inicio)
    # print(final)
    print('Fechas elegidas. Procedo a predecir.')
    predicciones = loaded.predict(start=inicio, end=final, dynamic=False, typ='levels').rename(
        'SARIMA(1,1,1)(2,0,3,24) Predicciones')
    print('Predicciones hechas.')
    prediccion = predicciones.to_csv('LaPrediccion.csv')
    print('Guardado en csv. Te lo mando.')

    # return predicciones
    return prediccion