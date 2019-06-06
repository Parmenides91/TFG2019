from django.db import models
from django.conf import settings
from django.urls import reverse

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime, timedelta

from . import func_parciales
from . import func_inmueble
from . import func_analisis_consumo
from . import func_datos_prediccion


from django.core.mail import send_mail

import os

# pip install misaka
import misaka

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Inmueble(models.Model):
    user=models.ForeignKey(User, related_name="inmuebles", on_delete=models.CASCADE)
    nombre=models.CharField(max_length=30, unique=True)
    descripcion=models.CharField(max_length=255, blank=True)
    created_at=models.DateTimeField(auto_now=True)
    consumo_inmueble=models.FileField(upload_to='consumosInmuebles', blank = False)
    consumo_inmueble_parcial=models.FileField(upload_to='consumosInmuebles', blank = True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("forecasting:single_inmueble", kwargs={"username":self.user.username, "pk":self.pk})

    def filename1(self):
        return os.path.basename(self.consumo_inmueble.name)

    def filename2(self):
        return os.path.basename(self.consumo_inmueble_parcial.name)

    # Unificar los consumos que tenga esta casa
    @property
    def unificar_consumos(self):
        """
        if self.consumo_inmueble==None and self.consumo_inmueble_parcial:
            self.consumo_inmueble=self.consumo_inmueble_parcial
            self.consumo_inmueble.save()
            self.consumo_inmueble_parcial.delete()
        elif self.consumo_inmueble and self.consumo_inmueble_parcial:
            pass
        else:
            pass
        """

        # """Prueba de que crear las predicciones funciona"""
        # modelos = ModeloConsumo.objects.all()
        # for modelo in modelos:
        #     print('Entramos a por los modelos a hacer predicciones, darling.')
        #     print('Fecha de creación:')
        #     print(modelo.created_at)
        #     print('Esa era la fecha.')
        #     print('A continuación te digo el fichero')
        #     print(modelo.fichero_modelo_inmueble.name)
        #     print('Ese es el fichero')
        #     nueva_prediccion = PrediccionConsumo.objects.create(modelo_consumo_origen=modelo,
        #                                                                fichero_prediccion_consumo=func_datos_prediccion.crearPrediccion(
        #                                                                    modelo.fichero_modelo_inmueble))
        #     print('Create() hecho. Vamos a guardar todo.')
        #     nueva_prediccion.save()
        #     print('Guardado.')
        #
        #     print('Ahora mando EMAILS.')
        #     send_mail(
        #         'Creación de Predicción',
        #         'Ha finalizado el proceso de creación de sus predicciones.',
        #         'from@example.com',
        #         [modelo.inmueble_origen.user.email],
        #         fail_silently=False,
        #     )
        # """Fin de la prueba de que la creación por cron de las predicciones funciona (o no, eso es lo que voy a comprobar)"""



        df = pd.read_csv(self.consumo_inmueble, delimiter=';', decimal=',')
        #df2 = pd.read_csv(self.consumo_inmueble_parcial, delimiter=';', decimal=',')
        """
        try:
            df2 = pd.read_csv(self.consumo_inmueble_parcial, delimiter=';', decimal=',')
        except:
            pass
        """

        info_inmueble = {'grafica_inmueble': func_inmueble.consumo_chart(df),}

        # #organizar consumos parciales
        # func_parciales.obtener_consumos_asociados(self.user_id, self.pk)

        return info_inmueble


class ConsumoParcial(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    inmueble_asociado=models.ForeignKey(Inmueble, related_name="consumosparciales", on_delete=models.CASCADE)
    fichero_consumo_parcial=models.FileField(upload_to='consumosParciales', blank = False)

    def __str__(self):
        return self.inmueble_asociado_id

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forecasting:single_inmueble', kwargs={"username":self.user.username, "pk":self.inmueble_asociado.pk})


class Consumo(models.Model):
    user = models.ForeignKey(User, related_name = "consumos", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now = True)
    titulo = models.CharField(max_length = 255, unique = True)
    fichero_consumo = models.FileField(upload_to='consumos', blank = False)
    coste_tarifa_PPP = models.DecimalField(default=0, max_digits=8, decimal_places=4)
    coste_tarifa_EDP = models.DecimalField(default=0, max_digits=8, decimal_places=4)
    coste_tarifa_VE = models.DecimalField(default=0, max_digits=8, decimal_places=4)

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "forecasting:single",
            kwargs={
                "username": self.user.username,
                "pk": self.pk
                }
            )

    def filename(self):
        return os.path.basename(self.fichero_consumo.name)



    # Método unificado para abrir el fichero y repartir el dataframe??
    @property
    def analisis_consumo(self):
        df = pd.read_csv(self.fichero_consumo, delimiter=';', decimal=',')

        info_consumo = {}

        # Gráfica del Consumo
        """
        info_consumo = {'grafica_consumo':func_analisis_consumo.consumo_chart(df),
                        'PVPCprecioPPP':func_analisis_consumo.peaje_por_defecto(df)}
        self.coste_tarifa_PPP = info_consumo.get('PVPCprecioPPP')
        """
        info_consumo = {'grafica_consumo': func_analisis_consumo.consumo_chart(df),
                        'PVPCprecios': func_analisis_consumo.obtener_precios_mercado_regulado(df)}

        self.coste_tarifa_PPP = info_consumo.get('PVPCprecios').get('PPD')
        self.coste_tarifa_EDP = info_consumo.get('PVPCprecios').get('EDP')
        self.coste_tarifa_VE = info_consumo.get('PVPCprecios').get('VE')

        return info_consumo


    """
    @property
    def consumo_chart(self):
        df = pd.read_csv(self.fichero_consumo, delimiter = ';', decimal=',')
        df = df.drop(["CUPS", "Metodo_obtencion"], axis=1)
        ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H') #secuencia de horas
        #df['Hora'] = df['Hora'].astype(str) + ':00'
        #df['Fecha'] = df['Fecha'] + ' ' + df['Hora']
        df['Fecha'] = ristra
        df = df.drop(["Hora"], axis=1)
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y %H:%M')

        n_leyenda = 'Consumo de ' + self.user.username

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
    """

    """
    @property
    def contra_peaje_por_defecto(self):
        if self.coste_tarifa_PPP == 0:
            #data = pd.read_csv(self.fichero_consumo, delimiter = ';', decimal=',')
            #self.coste_tarifa_PPP = func_tarifas.peaje_por_defecto(data)
            self.coste_tarifa_PPP = func_tarifas.peaje_por_defecto(self.fichero_consumo)
            return self.coste_tarifa_PPP
        else:
            return self.coste_tarifa_PPP
    """

class ModeloConsumo(models.Model):
    inmueble_origen=models.ForeignKey(Inmueble, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    fichero_modelo_inmueble = models.FileField(upload_to='modelos', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class PrediccionConsumo(models.Model):
    modelo_consumo_origen=models.ForeignKey(ModeloConsumo, on_delete=models.CASCADE)
    #created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    fichero_prediccion_consumo = models.FileField(upload_to='predicciones', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class ModeloPred(models.Model):
    consumo_origen = models.ForeignKey(Consumo, on_delete = models.CASCADE)
    created_by = models.ForeignKey(User, related_name = "modelosPred", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now = True)
    titulo = models.CharField(max_length = 255, unique = True)
    fichero_modeloPred = models.FileField(upload_to='modelos', blank = True)
    raizECM = models.DecimalField(default=0, max_digits=11, decimal_places=10)
    media = models.DecimalField(default=0, max_digits=11, decimal_places=10)

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "forecasting:single_MP",
            kwargs={
                "username": self.user.username,
                "pk": self.pk,
                }
            )

    def filename(self):
        return os.path.basename(self.fichero_modeloPred.name)

    # Creo el modelo que necesito y sus estadísitcas
    @property
    def creacion_modelo(self):
        if not (self.consumo_origen):
            df = pd.read_csv(self.consumo_origen, delimiter=';', decimal=',')
            ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H')
            df['Fecha'] = ristra
            df = df.drop(['CUPS', 'Hora', 'Metodo_obtencion'], axis=1)
            df.index = pd.to_datetime(df['Fecha'])
            df = df.drop(['Fecha'], axis=1)
            df.index.freq = 'h'

            return True
        else:
            return False



class Prediccion(models.Model):
    modelopred_origen = models.ForeignKey(ModeloPred, on_delete = models.CASCADE)
    created_by = models.ForeignKey(User, related_name = "predicciones", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now = True)
    titulo = models.CharField(max_length = 255, unique = True)
    fichero_prediccion = models.FileField(upload_to='predicciones', blank = True)
    #enviado=false

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "forecasting:single_PP",
            kwargs={
                "username": self.user.username,
                "pk": self.pk,
                }
            )

    # Predicción forzada del día de mañana
    """
    @property
    def prediccion_datos(self):
        # Fecha de inicio de la predicción
        inicioYear = datetime.now().__format__('%Y')
        inicioMonth = datetime.now().__format__('%m')
        inicioDay = datetime.now().__format__('%d')
        inicio = datetime(int(inicioYear), int(inicioMonth), int(inicioDay), 0, 0, 0)
        inicio += timedelta(days=1)
        iniPred = inicio
        # Fecha fin de predicción
        finalYear = datetime.now().__format__('%Y')
        finalMonth = datetime.now().__format__('%m')
        finalDay = datetime.now().__format__('%d')
        final = datetime(int(finalYear), int(finalMonth), int(finalDay), 23, 0, 0)
        for i in range(0):
            final += timedelta(days=1)
        final += timedelta(days=1)
        finPred = final

        if False:
            #Modelo creado a partir del consumo subido del usuario
            #modeloPrediccion = SARIMAXResults.load('model01.pkl')
            pass
        else:
            #Modelo genérico
            modeloPrediccion = SARIMAXResults.load('model01.pkl')

        predictions = modeloPrediccion.predict(start=iniPred, end=finPred, dynamic=False, typ='levels').rename('SARIMA(1,1,1)(2,0,3,24) Predictions')

        n_leyenda = 'Predicciones'
        trace1 = go.Scatter(
            x=predictions.index,
            y=predictions.values,
            mode='lines+markers',
            name=n_leyenda,
            marker=dict(color='rgb(0,0,255)', size=6, opacity=0.4))

        data = [trace1, ]

        layout = go.Layout(
            title='Consumo',
            showlegend=True,
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

        pred_dict = {'grafica_prediccion': plot_div}

        return pred_dict
        """

