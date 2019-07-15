import pandas as pd
import numpy as np
import plotly.graph_objs as go
from django.core.files.base import ContentFile
from plotly.offline import plot

from datetime import datetime, timedelta
from django.core.files import File

from django.conf import settings

from .funciones_basicas import id_random_generator

# Load specific forecasting tools
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAXResults


def crearPrediccion(fichero):
    print('Has entrado a la función')
    # print(File(fichero))
    print(fichero)
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
    ruta_fich = settings.MEDIA_ROOT + '\\predicciones\\'
    ruta_pred = ruta_fich+'prediccion'+id_random_generator()+'.csv'
    df.to_csv(ruta_pred)

    # prediccion = predicciones.to_csv('LaPrediccion.csv')
    print('Guardado en csv. Te lo mando.')

    # return predicciones
    return ruta_pred




#Reparte juego para crear las gráficas de predicción en distintas fases temporales
def crear_graficas_predicción(df):
    grafs_dict = {'horas': crear_grafica_generica(df, 'horario'),
                  'dias': crear_grafica_generica(df.resample('D').sum(), 'diario'),
                  'semanas': crear_grafica_generica(df.resample('W').sum(), 'semanal'),
                  'meses': crear_grafica_generica(df.resample('M').sum(), 'mensual')}
    return grafs_dict

#Gráfica genérica
def crear_grafica_generica(df, tipo):
    n_leyenda = 'Predicción '+tipo

    trace1 = go.Scatter(
        x=df.index,
        y=df['Consumo_kWh'],
        mode='lines+markers',
        name=n_leyenda,
        marker=dict(color='rgb(0,0,255)', size=6, opacity=0.4))

    data = [trace1, ]

    layout = go.Layout(
        title='',
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


# Representar la Predicción de Consumo sobre la Predicción de Precios del Mercado Regulado
def crear_graficas_superpuestas(df):
    n_leyenda = 'Predicción'

    trace1 = go.Scatter(
        x=df.index,
        y=df['Consumo_kWh'],
        mode='lines+markers',
        name='Consumo',
        marker=dict(color='rgb(143,55,169)', size=6, opacity=0.4))

    trace2 = go.Scatter(
        x=df.index,
        y=df['TPD'],
        mode='lines+markers',
        name='TPD',
        marker=dict(color='rgb(0,255,0)', size=6, opacity=0.4))

    trace3 = go.Scatter(
        x=df.index,
        y=df['EDP'],
        mode='lines+markers',
        name='EDP',
        marker=dict(color='rgb(255,0,0)', size=6, opacity=0.4))

    trace4 = go.Scatter(
        x=df.index,
        y=df['VE'],
        mode='lines+markers',
        name='VE',
        marker=dict(color='rgb(0,0,255)', size=6, opacity=0.4))

    data = [trace1, trace2, trace3, trace4]

    layout = go.Layout(
        title='Predicciónes de Consumo y Precios Mercado Regulado',
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


def crear_graficas_superpuestas_predicciones(df, tipo):
    n_leyenda = 'Predicciones'

    trace1 = go.Scatter(
        x=df.index,
        y=df['Consumo_kWh'],
        mode='lines+markers',
        name='Consumo',
        marker=dict(color='rgb(143,55,169)', size=6, opacity=0.4))

    trace2 = go.Scatter(
        x=df.index,
        y=df[tipo],
        mode='lines+markers',
        name=tipo,
        marker=dict(color='rgb(0,255,0)', size=6, opacity=0.4),
        yaxis='y2')


    data = [trace1, trace2]

    layout = go.Layout(
        title='Predicción de Consumo - Predicción del Mercado Regulado',
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
            # autoexpand=False,
            # l=100,
            # r=20,
            # t=110,
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
        ),
        yaxis2=dict(
            title='€/MW/h',
            showgrid=True,
            zeroline=False,
            showline=True,
            showticklabels=True,
            overlaying='y',
            side='right',
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div