#from . import models
from . import plots

import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd




# Representación del Consumo en una gráfica
def consumo_chart(df):
    df = df.drop(["CUPS", "Metodo_obtencion"], axis=1)
    ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H')  # secuencia de horas
    # df['Hora'] = df['Hora'].astype(str) + ':00'
    # df['Fecha'] = df['Fecha'] + ' ' + df['Hora']
    df['Fecha'] = ristra
    df = df.drop(["Hora"], axis=1)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y %H:%M')

    #n_leyenda = 'Consumo de ' + self.user.username
    n_leyenda = 'Consumo'

    trace1 = go.Scatter(
        x=df['Fecha'],
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


def obtener_precios_mercado_regulado(df):
    inicio_fecha = df['Fecha'][0]
    fin_fecha = df['Fecha'][(len(df) - 1)]
    precios_MR = plots.precios_pvpc(inicio_fecha, fin_fecha)

    coste_PPD = (calcular_coste_tarifa_MR(df, precios_MR['PPD'], 'PPD')) / 1000
    coste_EDP = (calcular_coste_tarifa_MR(df, precios_MR['EDP'], 'EDP')) / 1000
    coste_VE = (calcular_coste_tarifa_MR(df, precios_MR['VE'], 'VE')) / 1000

    coste_tarfias_MR = {'PPD':coste_PPD,
                        'EDP':coste_EDP,
                        'VE':coste_VE,}

    return coste_tarfias_MR


def calcular_coste_tarifa_MR(df, precios, tipo):
    if tipo == 'PPD':
        coste_PPD = 0
        for index, row in df.iterrows():
            if index < len(precios):
                coste_PPD += row['Consumo_kWh'] * precios[index]
            else:
                break
        return coste_PPD

    elif tipo == 'EDP':
        coste_EDP = 0
        for index, row in df.iterrows():
            if index < len(precios):
                coste_EDP += row['Consumo_kWh'] * precios[index]
            else:
                break
        return coste_EDP

    else:
        coste_VE = 0
        for index, row in df.iterrows():
            if index < len(precios):
                coste_VE += row['Consumo_kWh'] * precios[index]
            else:
                break
        return coste_VE


def calcular_coste_tarifa_ib_oh(df):
    for index, row in df.iterrows():
        pass
    return 0