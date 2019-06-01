from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views import generic
from django.views.generic import DeleteView, TemplateView, UpdateView

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# pip install django-braces
from braces.views import SelectRelatedMixin

from . import forms
from .forms import InmuebleForm
from . import models
from . import plots

from . models import ModeloPred
from . import func_datos_modelo
from . import func_parciales

import csv

import logging
logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model
User = get_user_model()


# Create your views here.

# INMUEBLES
#listado de los inmuebles, en general (probablemente me lo puedo cargar, porque sólo quiero listar por usuario)
class InmuebleList(SelectRelatedMixin, generic.ListView):
    model=models.Inmueble
    select_related = ("user", )

#listado de los inmuebles de un usuario en concreto
# (aquí creo que va la comprobación de si el usuario que está en el contexto de la página es el que está tratando de acceder a ver el listado de inmuebles)
class UserInmuebles(generic.ListView):
    model=models.Inmueble
    template_name = "forecasting/user_inmueble_list.html"

    def get_queryset(self):
        try:
            self.inmueble_user=User.objects.get(username__iexact=self.kwargs.get("username"))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.inmueble_user.inmuebles.all()

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context["inmueble_user"]=self.inmueble_user
        return context

#muestra un inmueble individual
class InmuebleDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Inmueble
    select_related = ("user",)

    """
    def pintarParcial(self):
        parciales=self.inmueble.consumosparciales.all()
        for parcial in parciales:
            df=pd.read_csv(parcial, delimiter=';', decimal=',')
        return df
    """

    def get_ConsumoParcial(self, model, select_related):
        func_parciales.obtener_consumos_asociados(select_related, model.pk)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact = self.kwargs.get("username"))

    """
    def get(self, request, *args, **kwargs):
        try:
            consumosparciales = models.ConsumoParcial.objects.filter(
                user=self.request.user,
                inmueble_asociado=self.inmueble_asociado.pk
            ).get()
        except:
            pass

        return super().get(request, *args, **kwargs)
    """

#crear un nuevo inmueble
class CreateInmueble(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('nombre', 'descripcion', 'consumo_inmueble')
    model = models.Inmueble

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        #form.instance.created_by = self.request.user
        self.object.save()
        return super().form_valid(form)

#modificar un inmueble ya creado
class InmuebleUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Inmueble
    fields=['nombre','descripcion']
    template_name_suffix = '_form_update'


#eliminar un inmueble
"""
    Esta vista requiere atención:
    - Debería redirigir al listado de los inmuebles que tenga el usuario. Hay que pasarle por argumento el username
"""
class DeleteInmueble(LoginRequiredMixin, DeleteView):
    model = models.Inmueble
    success_url = reverse_lazy('home')
    #success_url = reverse_lazy('forecasting:create_inmueble', kwargs={"username": self.user.username})


# CONSUMOS PARCIALES
#crear un nuevo consumo parcial
class CreateConsumoParcial(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('inmueble_asociado', 'fichero_consumo_parcial',)
    model = models.ConsumoParcial

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user

        fichero_parcial = self.object.fichero_consumo_parcial
        df_parcial=pd.read_csv(fichero_parcial, delimiter=';', decimal=',')
        ristra = pd.date_range(df_parcial['Fecha'][0], periods=len(df_parcial), freq='H')
        df_parcial['Fecha'] = ristra
        df_parcial.drop(["Hora"], axis=1, inplace=True)
        df_parcial['Fecha'] = pd.to_datetime(df_parcial['Fecha'], format='%d/%m/%Y %H:%M')
        #to_csv y guardo
        self.object.fichero_consumo_parcial=fichero_parcial

        self.object.save()
        return super().form_valid(form)


# CONSUMOS
class ConsumoList(SelectRelatedMixin, generic.ListView):
    model = models.Consumo
    select_related = ("user",)

class UserConsumos(generic.ListView):
    model = models.Consumo
    template_name = "forecasting/user_consumo_list.html"

    def get_queryset(self):
        try:
            #self.consumo_user = User.objects.prefecth_related("forecasting").get(username__iexact=self.kwargs.get("username"))
            self.consumo_user = User.objects.get(username__iexact=self.kwargs.get("username"))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.consumo_user.consumos.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["consumo_user"] = self.consumo_user
        return context

class ConsumoDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Consumo
    select_related = ("user",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact = self.kwargs.get("username"))

class CreateConsumo(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('titulo', 'fichero_consumo')
    model = models.Consumo

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class DeleteConsumo(LoginRequiredMixin, DeleteView):
    model = models.Consumo
    success_url = reverse_lazy('forecasting:all')





# MODELOS DE PREDICCIÓN
class ModeloPredList(SelectRelatedMixin, generic.ListView):
    model = models.ModeloPred
    #select_related = ("consumo_origen",)
    select_related = ("user", )

class UserModelosPred(generic.ListView):
    model = models.ModeloPred
    template_name = "forecasting/user_modelopred_list.html"

    def get_queryset(self):
        try:
            #self.consumo_user = User.objects.prefecth_related("forecasting").get(username__iexact=self.kwargs.get("username"))
            self.modelopred_user = User.objects.get(username__iexact=self.kwargs.get("username"))
        except User.DoesNotExist:
            raise Http404
        else:
            #return self.modelopred_user.consumos.all()
            return self.modelopred_user.modelosPred.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modelopred_user"] = self.modelopred_user
        return context

class ModeloPredDetail(SelectRelatedMixin, generic.DetailView):
    model = models.ModeloPred
    select_related = ("created_by",)

    if not model.fichero_modeloPred:
        csvData = [['Person', 'Age'], ['Peter', '22'], ['Jasmine', '21'], ['Sam', '24']]
        with open('person.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csvData)
        csvFile.close()

    def get_queryset(self):
        queryset = super().get_queryset()
        #return queryset.filter(user__username__iexact = self.kwargs.get("username"))
        #return queryset.filter(pk__iexact = self.kwargs.get("pk"))
        return queryset.filter(created_by__username__iexact = self.kwargs.get("username"))

class CreateModeloPred(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('titulo', 'consumo_origen')
    model = models.ModeloPred


    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        #self.object.consumo_origen = self.request.user
        form.instance.created_by = self.request.user
        self.object.save()
        return super().form_valid(form)

class DeleteModeloPred(LoginRequiredMixin, DeleteView):
    model = models.ModeloPred
    success_url = reverse_lazy('forecasting:all_MP')



# PREDICCIONES
class PrediccionList(SelectRelatedMixin, generic.ListView):
    model = models.Prediccion
    select_related = ("user", )

class UserPredicciones(generic.ListView):
    model = models.Prediccion
    template_name = "forecasting/user_prediccion_list.html"

    def get_queryset(self):
        try:
            self.prediccion_user = User.objects.get(username__iexact=self.kwargs.get("username"))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.prediccion_user.predicciones.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prediccion_user"] = self.prediccion_user
        return context

class PrediccionDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Prediccion
    select_related = ("created_by",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by__username__iexact = self.kwargs.get("username"))

class CreatePrediccion(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('titulo', 'modelopred_origen')
    model = models.Prediccion

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        form.instance.created_by = self.request.user
        self.object.save()
        return super().form_valid(form)

class DeletePrediccion(LoginRequiredMixin, DeleteView):
    model = models.Prediccion
    success_url = reverse_lazy('forecasting:all_PP')


def crear_fic_mod(request, pk):
    #model = models.ModeloPred
    #mo_actual = model.filter(pk = pk)

    #mo_actual = ModeloPred.objects.filter(pk=pk)
    #nombre = mo_actual['titulo']
    #nombre2 = mo_actual.titulo

    #tit = ModeloPred.objects.get(pk=pk).titulo

    #mo_actual.fichero_modeloPred =
    csvData = [['Person', 'Age'], ['Peter', '22'], ['Jasmine', '21'], ['Sam', '24'], ['Manolo', 39]]
    with open('person.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()

    #miModelo = ModeloPred.objects.get(pk=pk).consumo_origen.fichero_consumo
    #modelo_specs = func_datos_modelo.creacion_modelo(miModelo)

    modelo_specs = func_datos_modelo.creacion_modelo(ModeloPred.objects.get(pk=pk).consumo_origen.fichero_consumo)

    ModeloPred.objects.get(pk=pk).raizECM = modelo_specs.get('RECM')
    #ModeloPred.objects.get(pk=pk).mead = modelo_specs.get('M')
    ModeloPred.objects.get(pk=pk).media = modelo_specs.get('M')

    csvData = [['Person', 'Age'], ['Peter', '22'], ['Jasmine', '21'], ['Sam', '24'], [modelo_specs.get('RECM'), '99'], [modelo_specs.get('M'), '99']]
    with open('person02.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)
    csvFile.close()

    """
    # Abro y preparo el dataframe
    c_o = ModeloPred.objects.get(pk=pk).consumo_origen.fichero_consumo
    df = pd.read_csv(c_o, delimiter=';', decimal=',')
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

    model = SARIMAX(train['Consumo_kWh'], order=(1, 1, 1), seasonal_order=(2, 0, 3, 24))
    results = model.fit()
    """

    return True

    #User.ModeloPred.fichero_modeloPred = User.ModeloPred.consumo_origen
    #User.objects.get()



class PVPCView(TemplateView):
    template_name = 'forecasting/pvpc_chart.html'

    """
    def get_queryset(self):
        recib = self.kwargs['yearS']
        print('ATENTO AQUI QUE VIENE:')
        print(recib)
    """

    """
    def get(self, *args, **kwargs):
        print('Processing GET request in PVPCView')
        #resp = super().get(*args, **kwargs)
        if not self.kwargs['yearS'] or self.kwargs['monthS'] or self.kwargs['dayS'] or self.kwargs['yearF'] or self.kwargs['monthF'] or self.kwargs['dayF']:
            ahora = datetime.now().__format__('%Y-%m-%d')
            principio = ahora + 'T02:00:00'
            finalYear = datetime.now().__format__('%Y')
            finalMonth = datetime.now().__format__('%m')
            finalDay = datetime.now().__format__('%d')
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final += timedelta(days=1)
            final = final.isoformat('T')
        else:
            principioYear = self.kwargs['yearS']
            principioMonth = self.kwargs['monthS']
            principioDay = self.kwargs['dayS']
            principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
            principio = principio.isoformat('T')
            finalYear = self.kwargs['yearF']
            finalMonth = self.kwargs['monthF']
            finalDay = self.kwargs['dayF']
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final = final.isoformat('T')
    """



    def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        """
        ahora = datetime.now().__format__('%Y-%m-%d')
        principio = ahora + 'T02:00:00'
        finalYear = datetime.now().__format__('%Y')
        finalMonth = datetime.now().__format__('%m')
        finalDay = datetime.now().__format__('%d')
        final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
        final += timedelta(days=1)
        final = final.isoformat('T')
        """

        """
        if not (self.kwargs.get('yearS') or self.kwargs.get('monthS') or self.kwargs.get('dayS') or self.kwargs.get('yearF') or self.kwargs.get('monthF') or self.kwargs.get('dayF')):
            ahora = datetime.now().__format__('%Y-%m-%d')
            principio = ahora + 'T02:00:00'
            finalYear = datetime.now().__format__('%Y')
            finalMonth = datetime.now().__format__('%m')
            finalDay = datetime.now().__format__('%d')
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final += timedelta(days=1)
            final = final.isoformat('T')
        else:
            principioYear = self.kwargs['yearS']
            principioMonth = self.kwargs['monthS']
            principioDay = self.kwargs['dayS']
            principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
            principio = principio.isoformat('T')
            finalYear = self.kwargs['yearF']
            finalMonth = self.kwargs['monthF']
            finalDay = self.kwargs['dayF']
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final = final.isoformat('T')
        """


        if (self.kwargs.get('yearS') and self.kwargs.get('monthS') and self.kwargs.get('dayS') and self.kwargs.get('yearF') and self.kwargs.get('monthF') and self.kwargs.get('dayF')):
            #Me viene fecha de inicio y de final
            principioYear = self.kwargs['yearS']
            principioMonth = self.kwargs['monthS']
            principioDay = self.kwargs['dayS']
            principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
            principio = principio.isoformat('T')
            finalYear = self.kwargs['yearF']
            finalMonth = self.kwargs['monthF']
            finalDay = self.kwargs['dayF']
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final = final.isoformat('T')
        elif (self.kwargs.get('yearS') and self.kwargs.get('monthS') and self.kwargs.get('dayS')):
            #Me viene sólo un día
            principioYear = self.kwargs['yearS']
            principioMonth = self.kwargs['monthS']
            principioDay = self.kwargs['dayS']
            principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
            principio = principio.isoformat('T')
            final = datetime(int(principioYear), int(principioMonth), int(principioDay), 1, 0, 0)
            final += timedelta(days=1)
            final = final.isoformat('T')
        else:
            #No me viene fecha
            """
            ahora = datetime.now().__format__('%Y-%m-%d')
            principio = ahora + 'T02:00:00'
            finalYear = datetime.now().__format__('%Y')
            finalMonth = datetime.now().__format__('%m')
            finalDay = datetime.now().__format__('%d')
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final += timedelta(days=1)
            final = final.isoformat('T')
            """


            ahora = datetime.now().__format__('%Y-%m-%d')
            principio = ahora + 'T02:00:00'
            """
            final = datetime.date.today().__format__('%Y-%m-%d') + datetime.timedelta(days=1)
            """
            finalYear = datetime.now().__format__('%Y')
            finalMonth = datetime.now().__format__('%m')
            finalDay = datetime.now().__format__('%d')
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final += timedelta(days=1)
            final = final.isoformat('T')
            """
            final = str(ahora)
            final += timedelta(days=1)
            final = datetime(final, 1, 0, 0)
            final = final.isoformat('T')
            """

            """
            principio = '2019-05-05T02:00:00'
            final = '2019-05-06T01:00:00'
            """


        context = super(PVPCView, self).get_context_data(**kwargs)
        context['grafico_precio'] = plots.chart_precios_pvpc(principio, final)
        return context


class InformacionSmartMeters(TemplateView):
    template_name = 'forecasting/info_smartmeters.html'

class InformacionFactura(TemplateView):
    template_name = 'forecasting/info_factura.html'

class InformacionEnergiaSpain(TemplateView):
    template_name = 'forecasting/info_energia_spain.html'

