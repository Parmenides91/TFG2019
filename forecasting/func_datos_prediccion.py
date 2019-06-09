import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot

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

    #Creo un dataframe con los valores de las predicciones
    ristra=pd.date_range(start=inicio, end=final, freq='h')
    d={'Fecha':ristra, 'Consumo_kWh':predicciones}
    df=pd.DataFrame(data=d)
    prediccion = df.to_csv('LaPrediccion.csv')

    # prediccion = predicciones.to_csv('LaPrediccion.csv')
    print('Guardado en csv. Te lo mando.')

    # return predicciones
    return prediccion


def predicionconsumo_chart(df):

    n_leyenda = 'Predicción'

    trace1 = go.Scatter(
        x=df.index,
        y=df['Consumo_kWh'],
        mode='lines+markers',
        name=n_leyenda,
        marker=dict(color='rgb(0,0,255)', size=6, opacity=0.4))

    data = [trace1, ]

    layout = go.Layout(
        title='Consumo',
        showlegend=True,
        # width = 800,
        # height = 700,
        hovermode='closest',
        bargap=0,
        legend=dict(
            # orientation='h',
            x=0.2, y=1.1,
            traceorder='normal',
            font=dict(
                family='sans-serif',
                size=12,
                color='#000',
            ),
            bgcolor='#E2E2E2',
            bordercolor='#FFFFFF',
            borderwidth=2,
        ),
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        xaxis=dict(
            title='',
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickcolor='rgb(204, 204, 204)',
            tickwidth=2,
            ticklen=2,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            title='kW/h',
            showgrid=True,
            zeroline=False,
            showline=True,
            showticklabels=True,
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div