from django.conf import settings
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from datetime import datetime, timedelta
import pandas as pd

from .funciones_basicas import id_random_generator

# Para el Job que genera los modelos
def crearModeloMR(df, tipo):
    df.index.freq = 'H'

    # Limpio los datos
    filt_df = df.loc[:, tipo]
    low = .05
    high = .95
    quant_df_low = filt_df.quantile(low)
    quant_df_high = filt_df.quantile(high)

    for index, row in df.iterrows():
        if row[tipo] < quant_df_low:
            row[tipo] = quant_df_low
        elif row[tipo] > quant_df_high:
            row[tipo] = quant_df_high

    model = SARIMAX(df[tipo], order=(2, 1, 1), seasonal_order=(2, 0, 1, 24)).fit()

    ruta_fich = settings.MEDIA_ROOT + '\\modelosMR\\'
    ruta_modelo = ruta_fich + 'modeloMR' + id_random_generator() + '.pkl'
    model.save(ruta_modelo)

    print('Esto es lo que te paso:')
    print(ruta_modelo)

    return ruta_modelo


# Para el Job que genera las predicciones
def crearPrediccionMR(fichero_modelo, tipo):
    loaded = SARIMAXResults.load(fichero_modelo)

    DIAS_A_PREDECIR = 7

    inicio = datetime.today().__format__('%Y-%m-%d')  # Hoy
    final = datetime.today()
    for i in range(DIAS_A_PREDECIR):
        final += timedelta(days=1)
    final = final.__format__('%Y-%m-%d')  # x DÍAS EN ADELANTE

    inicio = datetime(2018, 3, 1, 0, 0, 0)  # fuerzo un día en concreto because boobs
    final = datetime(2018, 3, 7, 0, 0, 0)  # fuerzo un día en concreto because boobs

    predicciones = loaded.predict(start=inicio, end=final, dynamic=False, typ='levels').rename('SARIMA(2,1,1)(2,0,1,24) Predicciones')

    ristra = pd.date_range(start=inicio, end=final, freq='h')
    d = {'Fecha': ristra, tipo: predicciones}
    df = pd.DataFrame(data=d)
    ruta_fich = settings.MEDIA_ROOT + '\\prediccionesMR\\'
    ruta_pred = ruta_fich + 'prediccion' + id_random_generator() + '.csv'
    df.to_csv(ruta_pred)

    return ruta_pred


def crear_costes_mr_prediccion(df_consumo, df_precios, tipo):
    #deberían tener exactamente las mismas fechas como index, así que se genera una nueva columna con el precio
    df_merge = pd.merge(df_consumo, df_precios, how='inner', left_index=True, right_index=True)

    coste = 0

    if tipo == 'TPD':
        for index, row in df_merge.iterrows():
            coste += (row['TPD']) * row['Consumo_kWh']
    else:
        print('Realmente no deberías estar aquí #º')

    if tipo == 'EDP':
        for index, row in df_merge.iterrows():
            coste += (row['EDP']) * row['Consumo_kWh']
    else:
        print('Realmente no deberías estar aquí #2')

    if tipo == 'VE':
        for index, row in df_merge.iterrows():
            coste += (row['VE']) * row['Consumo_kWh']
    else:
        print('Realmente no deberías estar aquí #3')

    coste = coste / 1000

    return coste