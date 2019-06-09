#from . import models
from . import plots

import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot
import numpy as np
import pandas as pd
import csv

# Load specific forecasting tools
from statsmodels.tsa.statespace.sarimax import SARIMAX

from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
#from pmdarima import auto_arima



def crearModelo(fichero):
    print('Has llegado a la función, baby.')
    df = pd.read_csv(fichero, delimiter=';', decimal=',')
    ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H')
    df['Fecha'] = ristra
    df = df.drop(['CUPS', 'Hora', 'Metodo_obtencion'], axis=1)
    df.index = pd.to_datetime(df['Fecha'])
    df = df.drop(['Fecha'], axis=1)
    df.index.freq = 'h'

    # Limpio los datos
    filt_df = df.loc[:, 'Consumo_kWh']
    low = .05
    high = .95
    quant_df_low = filt_df.quantile(low)
    quant_df_high = filt_df.quantile(high)

    for index, row in df.iterrows():
        if row['Consumo_kWh'] < quant_df_low:
            row['Consumo_kWh'] = quant_df_low
        elif row['Consumo_kWh'] > quant_df_high:
            row['Consumo_kWh'] = quant_df_high

    # model = SARIMAX(df['Consumo_kWh'], order=(1, 1, 1), seasonal_order=(2, 0, 3, 24))
    # results = model.fit()
    print('A continuación calculo el modelo.')
    model = SARIMAX(df['Consumo_kWh'], order=(1, 1, 1), seasonal_order=(2, 0, 3, 24)).fit()
    print('Lo guardo.')
    #poner un random, o la echa, y así no se sobreescriben, concatenado y fuera
    saved = model.save('modeloXXX.pkl')
    print('Te lo paso guardado')

    return saved


# Crea el modelo desde el consumo que haya elegido el usuario
def creacion_modelo(consumo):
    df = pd.read_csv(consumo, delimiter=';', decimal=',')
    ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H')
    df['Fecha'] = ristra
    df = df.drop(['CUPS', 'Hora', 'Metodo_obtencion'], axis=1)
    df.index = pd.to_datetime(df['Fecha'])
    df = df.drop(['Fecha'], axis=1)
    df.index.freq = 'h'

    # Limpio los datos
    filt_df = df.loc[:, 'Consumo_kWh']
    low = .05
    high = .95
    quant_df_low = filt_df.quantile(low)
    quant_df_high = filt_df.quantile(high)

    for index, row in df.iterrows():
        if row['Consumo_kWh'] < quant_df_low:
            row['Consumo_kWh'] = quant_df_low
        elif row['Consumo_kWh'] > quant_df_high:
            row['Consumo_kWh'] = quant_df_high

    tam_total = len(df)
    tam_train = int(tam_total/0.8)
    tam_test = tam_total-tam_train

    train = df.iloc[:tam_train]
    test = df.iloc[tam_test:]

    # model = SARIMAX(train['Consumo_kWh'], order=(1, 1, 1), seasonal_order=(2, 0, 3, 24))
    # results = model.fit()

    csvData = [['Person', 'Age'], ['Peter', '22'], ['Jasmine', '21'], ['Sam', '24']]
    with open('personNN.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()

    # datos = {'RECM':0.15,'M':0.7}
    # return datos

    #return results
    return True