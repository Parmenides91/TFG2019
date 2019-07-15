from django.conf import settings
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot

from .funciones_basicas import id_random_generator
from . import models
from .plots import chart_precios_pvpc



# Recopilo los precios de las fechas que se necesitan y los dejo listos para pintar
def representar_precios_mr(fecha_inicio, fecha_fin):

    historicos = models.HistoricoMercadoRegulado.objects.all()
    graf_precios_mr = None

    for historico in historicos:
        df = pd.read_csv(historico.ruta_fichero, index_col=0, parse_dates=True)
        df.indexfreq='h'
        ini_mr = df.first_valid_index()
        fin_mr = df.last_valid_index()

        fecha_inicio = pd.to_datetime(fecha_inicio)
        fecha_fin = pd.to_datetime(fecha_fin)

        # print('Primera fecha del histórico: {}'.format(ini_mr))
        # print('Última fecha del histórico: {}'.format(fin_mr))
        # print('Inicio precios solicitados: {}'.format(fecha_inicio))
        # print('Fin precios solicitados: {}'.format(fecha_fin))

        if (fecha_inicio > ini_mr and fecha_inicio < fin_mr) and (fecha_fin > ini_mr and fecha_fin < fin_mr):
            # Tengo el rango que me piden en el histórico
            print('Tengo el rango que me piden en el histórico')
            df_select = df[fecha_inicio: fecha_fin]
            print('Procedo a organizar su representación')
            graf_precios_mr = representar_precios_historicos(df_select)
        else:
            # No tengo el rango que me piden. Se lo solicito al crawler
            print('No tengo el rango que me piden. Se lo solicito al crawler')
            fecha_inicio = fecha_inicio.isoformat('T')
            fecha_fin = fecha_fin.isoformat('T')
            graf_precios_mr = chart_precios_pvpc(fecha_inicio, fecha_fin)

        break # no debería haber más históricos, y de haberlos todos iban a hacer referencia al mismo fichero

    return graf_precios_mr



# Representación de los precios obtenidos del histórico
def representar_precios_historicos(df):
    trace1 = go.Scatter(
        x=df.index,
        y=df['TPD'],
        mode='lines+markers',
        name='Tarifa por defecto',
        marker=dict(color='rgb(255,0,0)', size=6, opacity=0.4))

    trace2 = go.Scatter(
        x=df.index,
        y=df['EDP'],
        mode='lines+markers',
        name='Eficiencia 2 periodos',
        marker=dict(color='rgb(0,111,255)', size=6, opacity=0.4))

    trace3 = go.Scatter(
        x=df.index,
        y=df['VE'],
        mode='lines+markers',
        name='Vehículo eléctrico',
        marker=dict(color='rgb(77,255,0)', size=6, opacity=0.4))

    data = [trace1, trace2, trace3, ]

    layout = go.Layout(
        title='Tarifas Mercado Regulado',
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
            title='€ MW/h',
            showgrid=True,
            zeroline=False,
            showline=True,
            showticklabels=True,
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div



# Para el Job que genera los modelos de cada tarifa
def crearModelosMRunicos(df, tipo):
    df.index.freq = 'h'

    # Limpio los datos
    filt_df = df.loc[:, tipo]
    low = .05
    high = .95
    quant_df_low = filt_df.quantile(low)
    quant_df_high = filt_df.quantile(high)

    # Quito valores que distorsionen
    for index, row in df.iterrows():
        if row[tipo] < quant_df_low:
            row[tipo] = quant_df_low
        elif row[tipo] > quant_df_high:
            row[tipo] = quant_df_high

    if (tipo == 'TPD'):
        model = SARIMAX(df[tipo], order=(3, 1, 1), seasonal_order=(2, 0, 1, 24)).fit()
        ruta_fich = settings.MEDIA_ROOT + '\\modelosMR\\'
        ruta_modelo = ruta_fich + 'modeloMR_' + tipo + '_' + id_random_generator() + '.pkl'
        model.save(ruta_modelo)
        # return model
        return ruta_modelo
    elif (tipo == 'EDP'):
        # model = SARIMAX(df[tipo], order=(1, 0, 0), seasonal_order=(2, 0, 0, 24)).fit()
        model = SARIMAX(df[tipo], order=(1, 1, 0), seasonal_order=(2, 0, 0, 24)).fit()
        ruta_fich = settings.MEDIA_ROOT + '\\modelosMR\\'
        ruta_modelo = ruta_fich + 'modeloMR_' + tipo + '_' + id_random_generator() + '.pkl'
        model.save(ruta_modelo)
        # return model
        return ruta_modelo
    elif (tipo == 'VE'):
        # model = SARIMAX(df[tipo], order=(2, 0, 0), seasonal_order=(2, 0, 0, 24)).fit()
        # model = SARIMAX(df[tipo], order=(2, 1, 0), seasonal_order=(2, 0, 1, 24)).fit()
        model = SARIMAX(df[tipo], order=(2, 0, 0), seasonal_order=(2, 0, 0, 24)).fit()
        ruta_fich = settings.MEDIA_ROOT + '\\modelosMR\\'
        ruta_modelo = ruta_fich + 'modeloMR_' + tipo + '_' + id_random_generator() + '.pkl'
        model.save(ruta_modelo)
        # return model
        return ruta_modelo
    else:
        # Algo ha salido mal.
        print('Algo ha salido mal.')

    return False


# Creo que ya me puedo cargar esta función, uso la de arriba.
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


# Para el Job que crea predicciones de precio de las tarifas del Mercado Regulado desde cada modelo
def crearPrediccionMRunico(modelo, tipo, rango):
    loaded = SARIMAXResults.load(modelo)

    inicio = pd.to_datetime(rango.get('principio'))
    final = pd.to_datetime(rango.get('final'))

    if tipo == 'TPD':
        predicciones = loaded.predict(start=inicio, end=final, dynamic=False, typ='levels').rename(
            'SARIMA(3,1,1)(2,0,1,24) Predicciones')
        ristra = pd.date_range(start=inicio, end=final, freq='h')
        d = {'Fecha': ristra, tipo: predicciones}
        df = pd.DataFrame(data=d)
        ruta_fich = settings.MEDIA_ROOT + '\\prediccionesMR\\'
        ruta_pred = ruta_fich + 'prediccionMR_' + tipo + '_' + id_random_generator() + '.csv'
        df.to_csv(ruta_pred)
        return ruta_pred
    elif tipo == 'EDP':
        predicciones = loaded.predict(start=inicio, end=final, dynamic=False, typ='levels').rename(
            'SARIMA(1,0,0)(2,0,0,24) Predicciones')
        ristra = pd.date_range(start=inicio, end=final, freq='h')
        d = {'Fecha': ristra, tipo: predicciones}
        df = pd.DataFrame(data=d)
        ruta_fich = settings.MEDIA_ROOT + '\\prediccionesMR\\'
        ruta_pred = ruta_fich + 'prediccionMR_' + tipo + '_' + id_random_generator() + '.csv'
        df.to_csv(ruta_pred)
        return ruta_pred
    elif tipo == 'VE':
        predicciones = loaded.predict(start=inicio, end=final, dynamic=False, typ='levels').rename(
            'SARIMA(2,0,0)(2,0,0,24) Predicciones')
        ristra = pd.date_range(start=inicio, end=final, freq='h')
        d = {'Fecha': ristra, tipo: predicciones}
        df = pd.DataFrame(data=d)
        ruta_fich = settings.MEDIA_ROOT + '\\prediccionesMR\\'
        ruta_pred = ruta_fich + 'prediccionMR_' + tipo + '_' + id_random_generator() + '.csv'
        df.to_csv(ruta_pred)
        return ruta_pred
    else:
        # Creación de modelos para tarifas que no se tienen en cuenta: NOPE.
        print('Creación de Predicciones unicas mercado regulado: error')

    return False


# Creo que lo he sustituido por el de arriba, chico.
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


# Calcula el coste de una predicción de consumo en base a la predicción TPD realizada y también me da los datos de ambas predicciones juntas para poder pitnarlas juntas
def calcular_coste_preCons_prePrec(df_consumo, df_precios, tipo):
    df_merge = pd.merge(df_consumo, df_precios, how='inner', left_index=True, right_index=True)

    coste = 0

    if tipo == 'TPD':
        # Tarifa TPD.
        print('Tarifa TPD.')
        for index, row in df_merge.iterrows():
            coste += (row['TPD']) * row['Consumo_kWh']
    elif tipo == 'EDP':
        # Tarifa EDP.
        print('Tarifa EDP.')
        for index, row in df_merge.iterrows():
            coste += (row['EDP']) * row['Consumo_kWh']
    elif tipo == 'VE':
         # Tarifa VE.
        print('Tarifa VE.')
        for index, row in df_merge.iterrows():
             coste += (row['VE']) * row['Consumo_kWh']
    else:
        print('func_mr.py: caso no soportado - error.')

    coste = coste / 1000  # porque viene en €/MW/h y el consumo está en kW/h

    info_coste = {'valor': coste,
                  'datos':df_merge}

    return info_coste


# creo que te puedes cargar esta función porque usas la de arriba, chico.
# para crear un coste asociado a un consumo predicho con un precio predicho
def crear_costes_mr_prediccion(df_consumo, df_precios, tipo):
    #deberían tener exactamente las mismas fechas como index, así que se genera una nueva columna con el precio
    df_merge = pd.merge(df_consumo, df_precios, how='inner', left_index=True, right_index=True)

    coste = 0

    if tipo == 'TPD':
        for index, row in df_merge.iterrows():
            coste += (row['TPD']) * row['Consumo_kWh']
    else:
        print('Realmente no deberías estar aquí #1')

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

    coste = coste / 1000 # porque viene en €/MW/h y el consumo está en kW/h

    return coste