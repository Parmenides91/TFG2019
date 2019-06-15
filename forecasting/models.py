from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError

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
from .func_inmueble import coste_tarifas_usuario, coste_tarifas_mr

from .func_datos_prediccion import crearPrediccion
from .func_datos_modelo import crearModelo


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
    # consumo_inmueble = models.BinaryField()
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
        #     print('Create() hecho. Vamos a guardar tod.')
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

        # # Prueba de guardado de los modelos. No se guardan (aunque sí se crean) y las predicciones no lo encuentran
        # inmuebles = Inmueble.objects.all()
        # for inmueble in inmuebles:
        #     # Método 2
        #     nuevo_modelo = ModeloConsumo.objects.create(inmueble_origen=inmueble)
        #     el_mode = crearModelo(inmueble.consumo_inmueble)
        #     # el_file = ContentFile(el_mode)
        #     # nuevo_modelo.fichero_modelo_inmueble.save('ElModelo', el_file)
        #     nuevo_modelo.fichero_modelo_inmueble.save('ElModelo', el_mode)
        #     #PON EL SAVE AQUÍ, CUANDO CONSIGA PASAR DEL PUNTO ANTERIOR



        #Prueba de ver si el cálculo de costes en el MR funciona:
        usuarios = User.objects.all()
        for usuario in usuarios:
            inmuebles = Inmueble.objects.filter(user=usuario)
            for inmueble in inmuebles:
                df_c = pd.read_csv(inmueble.consumo_inmueble, index_col='Fecha', parse_dates=True)
                # historico = models.HistoricoMercadoRegulado.objects.filter(id=1)
                # HistoricoMercadoRegulado.__new__()
                h = HistoricoMercadoRegulado()
                historico = h.precios_mr
                df_p = historico[df_c.first_valid_index(): df_c.last_valid_index()]

                df_merge = pd.merge(df_c, df_p, how='inner', left_index=True, right_index=True)

                costeTPD = 0
        #Hasta aquí la prueba


        # df=pd.read_csv(self.consumo_inmueble)
        # df=pd.read_csv(self.consumo_inmueble, index_col = ['Fecha'], parse_dates = True)
        df = pd.read_csv(self.consumo_inmueble.path, index_col = ['Fecha'], parse_dates = True)
        df.index.freq = 'H'
        # df = pd.read_csv(self.consumo_inmueble, delimiter=';', decimal=',')
        #df2 = pd.read_csv(self.consumo_inmueble_parcial, delimiter=';', decimal=',')
        """
        try:
            df2 = pd.read_csv(self.consumo_inmueble_parcial, delimiter=';', decimal=',')
        except:
            pass
        """

        info_inmueble = {'grafica_inmueble': func_inmueble.consumo_chart(df),
                         #'costes_tarifas_usuario': coste_tarifas_usuario(df),
                         }

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

    # Representar la predicción que se ha llevado a cabo
    @property
    def representar_prediccionconsumo(self):
        df = pd.read_csv('LaPrediccion.csv')
        info_predicionconsumo = {'grafica_prediccionconsumo': func_datos_prediccion.predicionconsumo_chart(df), }
        return info_predicionconsumo

# Tarifa personalizada del usuario
class TarifaElectrica(models.Model):
    user = models.ForeignKey(User, related_name="tarifaselectricas", on_delete=models.CASCADE)
    nombre = models.CharField(max_length = 255, unique = True)
    created_at = models.DateTimeField(auto_now=True)
    # hora_ini_uno = models.CharField(max_length = 5, blank=False) # formato 13:00 (5 caracteres)
    # duracion_uno = models.PositiveIntegerField(default = 1, blank=False)
    # precio_uno = models.DecimalField(default=1, max_digits=8, decimal_places=4, blank=False)
    # hora_ini_dos = models.CharField(max_length=5, blank=True)  # formato 13:00 (5 caracteres)
    # duracion_dos = models.PositiveIntegerField(blank=True)
    # precio_dos = models.DecimalField(max_digits=8, decimal_places=4, blank=True)
    hora_ini_periodo_gracia = models.CharField(default ='14:00', max_length = 5, blank=False) # formato 13:00 (5 caracteres)
    hora_fin_periodo_gracia = models.CharField(default ='20:00', max_length = 5, blank=False) # formato 13:00 (5 caracteres)
    precio_periodo_gracia = models.FloatField(default = 0, blank=False)
    precio_periodo_general = models.FloatField(default = 0, blank=False)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("forecasting:single_tarifaelectrica", kwargs={"username":self.user.username, "pk":self.pk})


#Relación entre un Inmueble y aplicar una de sus Tarifas Eléctricas
class CosteInmuebleTE(models.Model):
    inmueble_asociado = models.ForeignKey(Inmueble, on_delete=models.CASCADE)
    tarifalectrica_asociada = models.ForeignKey(TarifaElectrica, on_delete=models.CASCADE)
    # inmueble_asociado = models.OneToOneField(Inmueble, on_delete=models.CASCADE)
    # tarifalectrica_asociada = models.OneToOneField(TarifaElectrica, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now=True)
    actualizado = models.BooleanField(default=True)
    coste = models.FloatField()

    # class Meta:
    #     unique_together = (('inmueble_asociado', 'tarifalectrica_asociada'),)

#LA COMENTO PARA QUE NO ME TOQUE LOS HUEVOS CONSTANTEMENTE
# LA CLASE QUE GUARDA EL HISTÓRICO DE PRECIOS
FECHA_INICIO_PRECIOS=datetime(2019, 1, 1, 0, 0, 0).isoformat('T') # 2019-01-01 00:00:00
FECHA_FIN_PRECIOS=(datetime.now().__format__('%Y-%m-%d') ) + 'T00:00:00' # HOY
from . import plots
# def recolectarPrecio():
#     precios = plots.precios_pvpc(FECHA_INICIO_PRECIOS, FECHA_FIN_PRECIOS)
#     precios = pd.DataFrame(data=precios, )
#     pass

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
           cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

from django.core.files import File
ECHA_INICIO_PRECIOS=datetime(2018, 1, 1, 0, 0, 0).isoformat('T') # 2018-01-01 00:00:00
FECHA_FIN_PRECIOS=datetime(2019, 6, 13, 0, 0, 0).isoformat('T') # 2019-06-13 00:00:00
def leerHistorico():
    df = pd.read_csv('HistoricoPreciosMR.csv', index_col = 0, parse_dates = True)
    return df

class HistoricoMercadoRegulado(metaclass=Singleton):
    precios_mr = models.BinaryField(default=leerHistorico())
    # precios_mr = models.FileField(default=leerHistorico())
    # precios_luz = models.FileField(upload_to='preciosPVPC', blank=False, default=recolectarPrecio())
    primera_fecha=models.DateTimeField(blank=False, default=FECHA_INICIO_PRECIOS)
    ultima_fecha=models.DateTimeField(blank=False, default=FECHA_FIN_PRECIOS)
#HASTA AQUÍ


#Coste del consumo de un Inmueble en relación con los precios del Mercado Regulado
class CosteInmuebleMR(models.Model):
    inmueble_asociado = models.ForeignKey(Inmueble, on_delete=models.CASCADE)
    tipo = models.CharField(default='PPD', max_length=3, blank=False)
    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now=True)
    actualizado = models.BooleanField(default=True)
    coste = models.FloatField()


#Esto es el segundo pensamiento sobre cómo hacerlo
# FECHA_INICIO_PRECIOS=datetime(2019, 1, 1, 0, 0, 0).isoformat('T') # 2019-01-01 00:00:00
# FECHA_FIN_PRECIOS=(datetime.now().__format__('%Y-%m-%d') ) + 'T00:00:00' # HOY
# from . import plots
# def recolectarPrecio(creador):
#     ristra = pd.date_range(start=FECHA_INICIO_PRECIOS, end=FECHA_FIN_PRECIOS, freq='h')
#     precios = plots.precios_pvpc(FECHA_INICIO_PRECIOS, FECHA_FIN_PRECIOS)
#     d={'Fecha':ristra, 'PPP':precios['PPD'], 'EDP':precios['EDP'], 'VE':precios['VE']}
#     df = pd.DataFrame(data=d)
#     df = df.set_index('Fecha')
#     df = df.resample('H').interpolate(method='linear')
#     nombre=creador
#     ficheroMR = df.to_csv(nombre+'datosMR.csv')
#     return ficheroMR

# class HistoricoMercadoRegulado(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
#     precios_luz = models.FileField()
#     primera_fecha=models.DateTimeField()
#     ultima_fecha=models.DateTimeField()
#
#     # sobreescribo el método de escritura para que, si ya hay una instancia creada, no se creen más
#     def save(self, *args, **kwargs):
#         if HistoricoMercadoRegulado.objects.exists() and not self.pk:
#             # if you'll not check for self.pk
#             # then error will also raised in update of exists model
#             raise ValidationError('ERROR: sólo puedes crear un histórico.')
#         return super(HistoricoMercadoRegulado, self).save(*args, **kwargs)



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

