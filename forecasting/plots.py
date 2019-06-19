from . import *
from matplotlib import pyplot as plt

import json
import urllib
import pandas as pd
import numpy as np
import datetime
import pickle

import datetime
import glob
import os
import logging

import numpy as np
import plotly.graph_objs as go

from plotly.offline import plot

logger = logging.getLogger(__name__)



class ESIOS(object):

    def __init__(self, token):
        """
        Class constructor
        :param token: string given by the SIOS to you when asked to: Consultas Sios <consultasios@ree.es>
        """
        # The token is unique: You should ask for yours to: Consultas Sios <consultasios@ree.es>
        if token is None:
            print('The token is unique: You should ask for yours to: Consultas Sios <consultasios@ree.es>')
        self.token = token

        self.allowed_geo_id = [3, 8741]  # España y Peninsula

        # standard format of a date for a query
        self.dateformat = '%Y-%m-%dT%H:%M:%S'

        # dictionary of available series

        self.__offer_indicators_list = list()
        self.__analysis_indicators_list = list()
        self.__indicators_name__ = dict()
        self.available_series = dict()

        print('Getting the indicators...')
        self.available_series = self.get_indicators()

    def __get_headers__(self):
        """
        Prepares the CURL headers
        :return:
        """
        # Prepare the arguments of the call
        headers = dict()
        headers['Accept'] = 'application/json; application/vnd.esios-api-v1+json'
        headers['Content-Type'] = 'application/json'
        headers['Host'] = 'api.esios.ree.es'
        headers['Authorization'] = 'Token token=\"' + self.token + '\"'
        headers['Cookie'] = ''
        return headers

    def get_indicators(self):
        """
        Get the indicators and their name.
        The indicators are the indices assigned to the available data series
        :return:
        """
        fname = 'indicators.pickle'
        import os
        if os.path.exists(fname):
            # read the existing indicators file
            with open(fname, "rb") as input_file:
                all_indicators, self.__indicators_name__, self.__offer_indicators_list, self.__analysis_indicators_list = pickle.load(input_file)
        else:
            # create the indicators file querying the info to ESIOS
            """
            curl "https://api.esios.ree.es/offer_indicators" -X GET
            -H "Accept: application/json; application/vnd.esios-api-v1+json"
            -H "Content-Type: application/json"
            -H "Host: api.esios.ree.es"
            -H "Authorization: Token token=\"5c7f9ca844f598ab7b86bffcad08803f78e9fc5bf3036eef33b5888877a04e38\""
            -H "Cookie: "
            """
            all_indicators = dict()
            self.__indicators_name__ = dict()

            # This is how the URL is built
            url = 'https://api.esios.ree.es/offer_indicators'

            # Perform the call
            req = urllib.request.Request(url, headers=self.__get_headers__())
            with urllib.request.urlopen(req) as response:
                try:
                    json_data = response.read().decode('utf-8')
                except:
                    json_data = response.readall().decode('utf-8')

                result = json.loads(json_data)

            # fill the dictionary
            indicators = dict()
            self.__offer_indicators_list = list()
            for entry in result['indicators']:
                name = entry['name']
                id_ = entry['id']
                indicators[name] = id_
                self.__indicators_name__[id_] = name
                self.__offer_indicators_list.append([name, id_])

            all_indicators[u'indicadores de curvas de oferta'] = indicators

            """
            curl "https://api.esios.ree.es/indicators" -X GET
            -H "Accept: application/json; application/vnd.esios-api-v1+json"
            -H "Content-Type: application/json" -H "Host: api.esios.ree.es"
            -H "Authorization: Token token=\"5c7f9ca844f598ab7b86bffcad08803f78e9fc5bf3036eef33b5888877a04e38\""
            -H "Cookie: "
            """
            url = 'https://api.esios.ree.es/indicators'

            req = urllib.request.Request(url, headers=self.__get_headers__())
            with urllib.request.urlopen(req) as response:
                try:
                    json_data = response.read().decode('utf-8')
                except:
                    json_data = response.readall().decode('utf-8')
                result = json.loads(json_data)

            # continue filling the dictionary
            indicators = dict()
            self.__analysis_indicators_list = list()
            for entry in result['indicators']:
                name = entry['name']
                id_ = entry['id']
                indicators[name] = id_
                self.__indicators_name__[id_] = name
                self.__analysis_indicators_list.append([name, id_])

            all_indicators[u'indicadores de análisis '] = indicators

            # save the indictators
            with open(fname, "wb") as output_file:
                dta = [all_indicators, self.__indicators_name__, self.__offer_indicators_list, self.__analysis_indicators_list]
                pickle.dump(dta, output_file)

        return all_indicators

    def get_names(self, indicators_list):
        """
        Get a list of names of the given indicator indices
        :param indicators_list:
        :return:
        """
        names = list()
        for i in indicators_list:
            names.append(self.__indicators_name__[i])

        return np.array(names, dtype=np.object)

    def save_indicators_table(self, fname='indicadores.xlsx'):
        """
        Saves the list of indicators in an excel file for easy consultation
        :param fname:
        :return:
        """
        data = self.__offer_indicators_list + self.__analysis_indicators_list

        df = pd.DataFrame(data=data, columns=['Nombre', 'Indicador'])

        df.to_excel(fname)

    def __get_query_json__(self, indicator, start, end):
        """
        Get a JSON series
        :param indicator: series indicator
        :param start: Start date
        :param end: End date
        :return:
        """
        # This is how the URL is built

        #  https://www.esios.ree.es/es/analisis/1293?vis=2&start_date=21-06-2016T00%3A00&end_date=21-06-2016T23%3A50&compare_start_date=20-06-2016T00%3A00&groupby=minutes10&compare_indicators=545,544#JSON
        url = 'https://api.esios.ree.es/indicators/' + indicator + '?start_date=' + start + '&end_date=' + end

        # Perform the call
        req = urllib.request.Request(url, headers=self.__get_headers__())
        with urllib.request.urlopen(req) as response:
            try:
                json_data = response.read().decode('utf-8')
            except:
                json_data = response.readall().decode('utf-8')
            result = json.loads(json_data)

        return result

    def get_data(self, indicator, start, end):
        """
        :param indicator: Series indicator
        :param start: Start date
        :param end: End date
        :return:
        """
        # check types: Pass to string for the url
        if type(start) is datetime.datetime:
            start = start.strftime(self.dateformat)

        if type(end) is datetime.datetime:
            start = end.strftime(self.dateformat)

        if type(indicator) is int:
            indicator = str(indicator)

        # get the JSON data
        result = self.__get_query_json__(indicator, start, end)

        # transform the data
        d = result['indicator']['values']  # dictionary of values

        if len(d) > 0:
            hdr = list(d[0].keys())  # headers
            data = np.empty((len(d), len(hdr)), dtype=np.object)

            for i in range(len(d)):  # iterate the data entries
                for j in range(len(hdr)):  # iterate the headers
                    h = hdr[j]
                    val = d[i][h]
                    data[i, j] = val

            df = pd.DataFrame(data=data, columns=hdr)  # make the DataFrame

            df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])  # convert to datetime

            df = df.set_index('datetime_utc')  # Set the index column

            del df.index.name  # to avoid the index name bullshit

            return df
        else:
            return None

    def get_multiple_series(self, indicators, start, end):
        """
        Get multiple series data
        :param indicators: List of indicators
        :param start: Start date
        :param end: End date
        :return:
        """
        df = None
        df_list = list()
        names = list()
        for i in range(len(indicators)):

            name = self.__indicators_name__[indicators[i]]
            names.append(name)
            print('Parsing ' + name)
            if i == 0:
                # Assign the first indicator
                df = self.get_data(indicators[i], start, end)
                df = df[df['geo_id'].isin(self.allowed_geo_id)]  # select by geography
                df.rename(columns={'value': name}, inplace=True)
                df_list.append(df)
            else:
                # merge the newer indicators
                df_new = self.get_data(indicators[i], start, end)
                if df_new is not None:
                    df_new = df_new[df_new['geo_id'].isin(self.allowed_geo_id)]  # select by geography
                    df_new.rename(columns={'value': name}, inplace=True)
#                    df = df.join(df_new[[name, 'datetime']], how='left', lsuffix='d'+name)
                    df = df.join(df_new[name])
                df_list.append(df_new)

        return df, df_list, names


# Para conocer el precio entre las fechas que se soliciten
def precios_pvpc(a, b):
    #start_ = '2019-05-04T02:00:00'
    #end_ = '2019-05-05T01:00:00'
    start_ = a
    end_ = b

    # The token is unique: You should ask for yours to: Consultas Sios <consultasios@ree.es>

    token = '859b2fc71fb5898354fe9e4b597f42b6fb30cd4c7ebc59aaefdeb95acf835659'
    esios = ESIOS(token)

    # esios.save_indicators_table()

    #    indicators_ = [600, 672, 673, 674, 675, 676, 677, 680, 681, 682, 683, 767, 1192, 1193, 1293]
    indicators_ = list()
    indicators_.append(1013)  # Precio de Regulación Secundaria subir
    indicators_.append(1014)  # Precio de Regulación Secundaria bajar
    indicators_.append(1015)  # Precio mercado SPOT Diario
    indicators_.append(1293)  # Demanda real
    names = esios.get_names(indicators_)
    dfmul, df_list, names = esios.get_multiple_series(indicators_, start_, end_)
    df = dfmul[names]  # get the actual series and neglect the rest of the info

    # precios = {'PPD':df[names[0]].values,
    #            'EDP':df[names[1]].values,
    #            'VE':df[names[2]].values,}

    info = {'Fecha': df[names[0]].index, 'TPD': df[names[0]].values, 'EDP': df[names[1]].values,
            'VE': df[names[2]].values, }
    daframe = pd.DataFrame(data=info)

    """
    if tipo == 'PPD':
        return df[names[0]].values
    elif tipo == 'EDP':
        return df[names[1]].values
    else:
        return df[names[2]].values
    """

    # return precios
    return daframe


# Para pintar los precios de las fechas que se le pasen
def chart_precios_pvpc(a, b):
    # start_ = '2019-06-13T02:00:00'
    # end_ = '2019-06-14T01:00:00'
    start_ = '2017-12-31T02:00:00'
    end_ = '2019-06-14T01:00:00'
    # start_ = a
    # end_ = b

    # The token is unique: You should ask for yours to: Consultas Sios <consultasios@ree.es>

    token = '859b2fc71fb5898354fe9e4b597f42b6fb30cd4c7ebc59aaefdeb95acf835659'
    esios = ESIOS(token)

    # esios.save_indicators_table()

    #    indicators_ = [600, 672, 673, 674, 675, 676, 677, 680, 681, 682, 683, 767, 1192, 1193, 1293]
    indicators_ = list()
    indicators_.append(1013)  # Precio de Regulación Secundaria subir
    indicators_.append(1014)  # Precio de Regulación Secundaria bajar
    indicators_.append(1015)  # Precio mercado SPOT Diario
    #indicators_.append(1293)  # Demanda real
    names = esios.get_names(indicators_)
    dfmul, df_list, names = esios.get_multiple_series(indicators_, start_, end_)
    df = dfmul[names]  # get the actual series and neglect the rest of the info

    #t = np.linspace(-1, 1, 2000)
    #y = (t**2) + (0.5 * np.random.randn(2000))
    #x = ['2019-05-04T00:00:00','2019-05-04T01:00:00', '2019-05-04T02:00:00', '2019-05-04T03:00:00','2019-05-04T04:00:00', '2019-05-04T05:00:00', '2019-05-04T06:00:00','2019-05-04T07:00:00', '2019-05-04T08:00:00', '2019-05-04T09:00:00','2019-05-04T10:00:00', '2019-05-04T11:00:00', '2019-05-04T12:00:00','2019-05-04T13:00:00', '2019-05-04T14:00:00', '2019-05-04T15:00:00','2019-05-04T16:00:00', '2019-05-04T17:00:00', '2019-05-04T18:00:00','2019-05-04T19:00:00', '2019-05-04T20:00:00', '2019-05-04T21:00:00','2019-05-04T22:00:00', '2019-05-04T23:00:00',]
    #dt.T
    #ristra = (df[names[0]].index).to_series()

    info = {'Fecha':df[names[0]].index, 'TPD':df[names[0]].values, 'EDP':df[names[1]].values, 'VE':df[names[2]].values,}
    daframe = pd.DataFrame(data=info)
    csvPrecios = daframe.to_csv('historicoMR.csv')

    # ristra = (df[names[0]].index).tz_convert('Etc/GMT-1')
    ristra = (df[names[0]].index)

    #ristra.to_series(keep_tz=False)
    trace1 = go.Scatter(
        x = ristra,
        y = df[names[0]].values,
        mode = 'lines+markers',
        name = 'Tarifa por defecto',
        marker = dict(color = 'rgb(255,0,0)', size = 6, opacity = 0.4))

    trace2 = go.Scatter(
        x=ristra,
        y=df[names[1]].values,
        mode='lines+markers',
        name='Eficiencia 2 periodos',
        marker=dict(color='rgb(0,111,255)', size=6, opacity=0.4))

    trace3 = go.Scatter(
        x=ristra,
        y=df[names[2]].values,
        mode='lines+markers',
        name='Vehículo eléctrico',
        marker=dict(color='rgb(77,255,0)', size=6, opacity=0.4))

    data = [trace1, trace2, trace3,]

    layout = go.Layout(
        title = 'Tarifas PVPC',
        showlegend = True,
        #width = 800,
        #height = 700,
        hovermode = 'closest',
        bargap = 0,
        legend = dict(
            #orientation='h',
            x=0.2, y=1.1,
            traceorder = 'normal',
            font=dict(
                family='sans-serif',
                size=12,
                color='#000',
            ),
            bgcolor='#E2E2E2',
            bordercolor='#FFFFFF',
            borderwidth=2,
        ),
        margin = dict(
            autoexpand = False,
            l = 100,
            r = 20,
            t = 110,
        ),
        xaxis = dict(
            title = '',
            showline = True,
            showgrid = True,
            showticklabels = True,
            linecolor = 'rgb(204, 204, 204)',
            linewidth = 2,
            ticks = 'outside',
            tickcolor = 'rgb(204, 204, 204)',
            tickwidth = 2,
            ticklen = 2,
            tickfont = dict(
                family = 'Arial',
                size = 12,
                color = 'rgb(82, 82, 82)',
            ),
        ),
        yaxis = dict(
            title = '€ MW/h',
            showgrid = True,
            zeroline = False,
            showline = True,
            showticklabels = True,
        )
    )


    fig = go.Figure(data = data, layout = layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs = False)
    return plot_div





# Pintar gráficas de los ficheros de consumo
def graf_consumo():

    t = np.linspace(-1, 1, 2000)
    x = (t**2) + (0.5 * np.random.randn(2000))
    y = (t**2) + (0.5 * np.random.randn(2000))

    trace1 = go.Scatter(
        x=x, y=y, mode='markers', name='points',
        marker=dict(color='rgb(0,0,0)', size=2, opacity=0.4)
    )
    trace2 = go.Histogram2d(
        x=x, y=y, name='density',
        nbinsx=100, nbinsy=100,
        colorscale='Jet', reversescale=False, showscale=True
    )
    trace3 = go.Histogram(
        x=x, name='x density',
        marker=dict(color='blue'),
        yaxis='y2'
    )
    trace4 = go.Histogram(
        y=y, name='y density', marker=dict(color='blue'),
        xaxis='x2'
    )
    data = [trace1, trace2, trace3, trace4]

    layout = go.Layout(
        showlegend=False,
        autosize=False,
        width=800,
        height=700,
        xaxis=dict(
            domain=[0, 0.85],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            domain=[0, 0.85],
            showgrid=False,
            zeroline=False
        ),
        margin=dict(
            t=50
        ),
        hovermode='closest',
        bargap=0,
        xaxis2=dict(
            domain=[0.85, 1],
            showgrid=False,
            zeroline=False
        ),
        yaxis2=dict(
            domain=[0.85, 1],
            showgrid=False,
            zeroline=False
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
