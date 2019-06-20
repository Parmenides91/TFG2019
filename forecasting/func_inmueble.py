#from . import models
from . import plots
from . import models

import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd

#Reparte juego para crear las gráficas en distintas fases temporales
def crear_graficas_inmueble(df):
    grafs_dict = {'horas': crear_grafica_generica(df, 'horario'),
                  'dias': crear_grafica_generica(df.resample('D').sum(), 'diario'),
                  'semanas': crear_grafica_generica(df.resample('W').sum(), 'semanal'),
                  'meses': crear_grafica_generica(df.resample('M').sum(), 'mensual')}
    return grafs_dict

#Gráfica genérica
def crear_grafica_generica(df, tipo):
    n_leyenda = 'Consumo '+tipo

    trace1 = go.Scatter(
        # x=df['Fecha'],
        x=df.index,
        y=df['Consumo_kWh'],
        mode='lines+markers',
        name=n_leyenda,
        marker=dict(color='rgb(0,0,255)', size=6, opacity=0.4))

    data = [trace1, ]

    layout = go.Layout(
        title='',
        showlegend=True,
        autosize = True,
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






# Representación del Consumo en una gráfica
def consumo_chart(df):
    # df = df.drop(["CUPS", "Metodo_obtencion"], axis=1)
    #     # ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H')  # secuencia de horas
    #     # # df['Hora'] = df['Hora'].astype(str) + ':00'
    #     # # df['Fecha'] = df['Fecha'] + ' ' + df['Hora']
    #     # df['Fecha'] = ristra
    #     # df = df.drop(["Hora"], axis=1)
    #     # df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y %H:%M')

    #n_leyenda = 'Consumo de ' + self.user.username
    n_leyenda = 'Consumo'

    trace1 = go.Scatter(
        # x=df['Fecha'],
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


# Cálculo del coste del consumo del inmueble mediante las tarifas personalizadas que haya creado el usuario
def coste_tarifas_usuario(df, tarifaelectrica):
    # df = pd.read_csv(fichero, index_col=['Fecha'], parse_dates=True)
    # df.index.freq = 'H'

    coste_periodo_gracia = 0
    for index, row in df.between_time(tarifaelectrica.hora_ini_periodo_gracia, tarifaelectrica.hora_fin_periodo_gracia).iterrows():
        coste_periodo_gracia += row['Consumo_kWh'] * tarifaelectrica.precio_periodo_gracia

    coste_periodo_general = 0
    for index, row in df.between_time(tarifaelectrica.hora_ini_periodo_gracia, tarifaelectrica.hora_fin_periodo_gracia, include_start=False,
                                          include_end=False).iterrows():
        coste_periodo_general += row['Consumo_kWh'] * tarifaelectrica.precio_periodo_general

    return coste_periodo_gracia + coste_periodo_general


    # tarifaselectricas = models.TarifaElectrica.objects.all()
    # costes_dict = {}
    # i = 0
    # for tarifaelectrica in tarifaselectricas:
    #     # coste_uno = df['Consumo_kWh'] * float(tarifaelectrica.precio_uno)
    #     # coste_dos = df['Consumo_kWh'] * float(tarifaelectrica.precio_dos)
    #
    #     # coste_uno = 0
    #     # for index, row in df.iterrows():
    #     #     coste_uno += row['Consumo_kWh'] * float(tarifaelectrica.precio_uno)
    #     # coste_dos = 0
    #     # for index, row in df.iterrows():
    #     #     coste_dos += row['Consumo_kWh'] * float(tarifaelectrica.precio_dos)
    #     #
    #     # coste_final = coste_uno+coste_dos
    #
    #     coste_periodo_gracia = 0
    #     for index, row in df.between_time(tarifaelectrica.hora_ini_periodo_gracia, tarifaelectrica.hora_fin_periodo_gracia).iterrows():
    #         coste_periodo_gracia += row['Consumo_kWh'] * tarifaelectrica.precio_periodo_gracia
    #
    #     coste_periodo_general = 0
    #     for index, row in df.between_time(tarifaelectrica.hora_ini_periodo_gracia, tarifaelectrica.hora_fin_periodo_gracia, include_start=False,
    #                                       include_end=False).iterrows():
    #         coste_periodo_general += row['Consumo_kWh'] * tarifaelectrica.precio_periodo_general
    #
    #     coste_final = coste_periodo_gracia + coste_periodo_general
    #
    #     coste_tarifa={'Tarifa':tarifaelectrica.nombre, 'Coste':coste_final}
    #
    #     costes_dict.update({i:coste_tarifa})
    #     i += 1
    #
    # return costes_dict


def coste_tarifas_MR(df_c, df_p):
    # print(df_c.index)
    # df_c.index = pd.to_datetime(df_c['Fecha'])
    # df_c.index.freq = 'h'
    # df_c = df_c.drop('Fecha', axis=1)
    df_p.index = df_c.index
    df_combinado = df_c.join(df_p[['TPD', 'EDP', 'VE']])

    costeTPD = 0
    costeEDP = 0
    costeVE = 0
    for index, row in df_combinado.iterrows():
        costeTPD += (row['TPD']) * row['Consumo_kWh']
        costeEDP += (row['EDP']) * row['Consumo_kWh']
        costeVE += (row['VE']) * row['Consumo_kWh']

    costeTPD = costeTPD / 1000
    costeEDP = costeEDP / 1000
    costeVE = costeVE / 1000

    costes = {'TPD':costeTPD, 'EDP':costeEDP, 'VE':costeVE}

    return costes


# Cálculo del coste del consumo del inmueble mediante los precios del mercado regulado
def coste_tarifas_mr(df):
    pass