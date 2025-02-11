"""
.. module:: view
    :synopsis: Contiene todas las vistas de la app forecasting.

.. moduleauthor:: Roberto Benéitez Vaquero


"""


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views import generic
from django.views.generic import DeleteView, TemplateView, UpdateView

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from django.core.files import File

# pip install django-braces
from braces.views import SelectRelatedMixin

from . import forms
from .forms import InmuebleForm
from . import models
from . import plots

from . models import ModeloPred
from . import func_datos_modelo
from . import func_parciales
from .funciones_basicas import limpiarCSV, id_random_generator
from .func_mr import representar_precios_mr

import csv

import logging
logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model
User = get_user_model()


# Create your views here.

# INMUEBLES
#listado de los inmuebles, en general (probablemente me lo puedo cargar, porque sólo quiero listar por usuario)
class InmuebleList(SelectRelatedMixin, generic.ListView):
    """
    Listado de los Inmuebles.
    """

    model=models.Inmueble
    select_related = ("user", )

#listado de los inmuebles de un usuario en concreto
# (aquí creo que va la comprobación de si el usuario que está en el contexto de la página es el que está tratando de acceder a ver el listado de inmuebles)

class UserInmuebles(generic.ListView):
    """
    Listado de los Inmuebles para un usuario en concreto.
    """

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
    """
    Muestra de los datos para un Inmueble en concreto.
    """

    model = models.Inmueble
    select_related = ("user",)

    # """
    # def pintarParcial(self):
    #     parciales=self.inmueble.consumosparciales.all()
    #     for parcial in parciales:
    #         df=pd.read_csv(parcial, delimiter=';', decimal=',')
    #     return df
    # """

    def get_ConsumoParcial(self, model, select_related):
        func_parciales.obtener_consumos_asociados(select_related, model.pk)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact = self.kwargs.get("username"))

    # """
    # def get(self, request, *args, **kwargs):
    #     try:
    #         consumosparciales = models.ConsumoParcial.objects.filter(
    #             user=self.request.user,
    #             inmueble_asociado=self.inmueble_asociado.pk
    #         ).get()
    #     except:
    #         pass
    #
    #     return super().get(request, *args, **kwargs)
    # """

FECHA_INICIO_PRECIOS=datetime(2019, 1, 1, 0, 0, 0).isoformat('T') # 2019-01-01 00:00:00
FECHA_FIN_PRECIOS=(datetime.now().__format__('%Y-%m-%d') ) + 'T00:00:00' # HOY
from . import plots
def recolectarPrecio(creador):
    ristra = pd.date_range(start=FECHA_INICIO_PRECIOS, end=FECHA_FIN_PRECIOS, freq='h')
    precios = plots.precios_pvpc(FECHA_INICIO_PRECIOS, FECHA_FIN_PRECIOS)
    d={'Fecha':ristra, 'PPP':precios['PPD'], 'EDP':precios['EDP'], 'VE':precios['VE']}
    df = pd.DataFrame(data=d)
    df = df.set_index('Fecha')
    df = df.resample('H').interpolate(method='linear')
    nombre=creador
    ficheroMR = df.to_csv(nombre+'datosMR.csv')
    return ficheroMR

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
#crear un nuevo inmueble
class CreateInmueble(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    """
    Creación de un Inmueble
    """

    fields = ('nombre', 'descripcion', 'consumo_inmueble')
    model = models.Inmueble

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        #form.instance.created_by = self.request.user

        #Haciéndolo de esta manera, la instancia no encuentra su fichero. YA SÍ QUE ESTÁ BIEN HECHO. NO MAMES, WEY
        df_inmueble=pd.read_csv(self.object.consumo_inmueble, delimiter=';', decimal=',')
        df_inmueble=limpiarCSV(df_inmueble)
        #TOD GUARDAR EL DATAFRAME EN UN PICKLE EN LUGAR DE EN CSV --> modificar el modelo
        # dire=os.path.join(settings.MEDIA_ROOT, 'consumosInmuebles')
        # # dire = os.path.join(str(FileSystemStorage.location), 'consumosInmuebles')
        # dire=os.path.join(dire, self.object.consumo_inmueble.name)
        # fichero_df_inmueble=df_inmueble.to_csv(dire)
        # fichero_df_inmueble=df_inmueble.to_csv(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'\\media\\consumosInmuebles\\'+self.object.consumo_inmueble.name)
        file_path=settings.MEDIA_ROOT+'\\consumosInmuebles\\'+self.object.consumo_inmueble.name

        # self.object.consumo_inmueble.file= ContentFile(df_inmueble.to_csv(columns={'Fecha','Consumo_kWh'}))
        self.object.consumo_inmueble.file = ContentFile(df_inmueble.to_csv(columns={'Consumo_kWh',}))
        file_path2 = settings.MEDIA_ROOT+'\\consumosInmuebles\\'+'ConInm'+id_random_generator()+'.csv'
        df_inmueble.to_csv(file_path2)
        self.object.consumo_inmueble_string =file_path2


        # #Cuando se crea un inmueble se crea un histórico de precios de la luz en el Mercado Regulado
        # nuevo_historicoMR = models.HistoricoMercadoRegulado.objects.create(user=self.request.user,
        #                                                                    precios_luz=recolectarPrecio(
        #                                                                        self.request.user),
        #                                                                    primera_fecha=FECHA_INICIO_PRECIOS,
        #                                                                    ultima_fecha=FECHA_FIN_PRECIOS)
        # nuevo_historicoMR.save()

        self.object.save()
        return super().form_valid(form)

#modificar un inmueble ya creado
class InmuebleUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modificación de los datos de un Inmueble.
    """

    model = models.Inmueble
    fields=['nombre','descripcion']
    template_name_suffix = '_form_update'


#eliminar un inmueble
# """
#     Esta vista requiere atención:
#     - Debería redirigir al listado de los inmuebles que tenga el usuario. Hay que pasarle por argumento el username
# """
class DeleteInmueble(LoginRequiredMixin, DeleteView):
    """
    Eliminación de un Inmueble
    """

    model = models.Inmueble
    success_url = reverse_lazy('home')
    #success_url = reverse_lazy('forecasting:create_inmueble', kwargs={"username": self.user.username})


# CONSUMOS PARCIALES
#crear un nuevo consumo parcial
class CreateConsumoParcial(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    """
    Creación de un consumo parcial asociado a un Inmueble en concreto.
    """

    fields = ('inmueble_asociado', 'fichero_consumo_parcial',)
    model = models.ConsumoParcial

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user

        # fichero_parcial = self.object.fichero_consumo_parcial
        # df_parcial=pd.read_csv(fichero_parcial, delimiter=';', decimal=',')
        # ristra = pd.date_range(df_parcial['Fecha'][0], periods=len(df_parcial), freq='H')
        # df_parcial['Fecha'] = ristra
        # df_parcial.drop(["Hora"], axis=1, inplace=True)
        # df_parcial['Fecha'] = pd.to_datetime(df_parcial['Fecha'], format='%d/%m/%Y %H:%M')
        # #to_csv y guardo
        # self.object.fichero_consumo_parcial=fichero_parcial

        df_parcial = pd.read_csv(self.object.fichero_consumo_parcial, delimiter=';', decimal=',')
        df_parcial = limpiarCSV(df_parcial)
        file_path = settings.MEDIA_ROOT + '\\consumosParciales\\' + self.object.fichero_consumo_parcial.name #me sobra???
        # self.object.fichero_consumo_parcial.file = ContentFile(df_parcial.to_csv(columns={'Fecha', 'Consumo_kWh'}))
        self.object.fichero_consumo_parcial.file = ContentFile(df_parcial.to_csv(columns={'Consumo_kWh',}))

        self.object.save()
        return super().form_valid(form)


# PREDICCIONES DE CONSUMO
#ver una predicción de consumo concreta
class PrediccionConsumoDetail(SelectRelatedMixin, generic.DetailView):
    """
    Visualización de los datos de una predicción de consumo en concreto.
    """

    model = models.PrediccionConsumo
    select_related = ("modelo_consumo_origen",)

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(created_by__username__iexact=self.kwargs.get("username"))

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(id__iexact=self.kwargs.get("pk"))

#TOD debería redigirigr al inmueble
#Para eliminar manualmente las predicciones de consumo
class DeletePrediccionConsumo(LoginRequiredMixin, DeleteView):
    """
    Eliminación de una predicción de consumo en concreto.
    """

    model = models.PrediccionConsumo
    success_url = reverse_lazy('home')

    # #Aviso al Inmueble que la predicción ha dejado de estar actualizada (porque me la he cargado, claramente)
    # def delete(self, request, *args, **kwargs):
    #     # self.object.modelo_consumo_origen.inmueble_origen.prediccion_actualizada=False
    #     return super(DeletePrediccionConsumo, self).delete(*args, **kwargs)


# TARIFA ELÉCTRICA
#crear una tarifa eléctrica
class CreateTarifaElectrica(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    """
    Creación de una tarifa eléctrica personalizada para el usuario.
    """

    fields = ('nombre', 'hora_ini_periodo_gracia', 'hora_fin_periodo_gracia', 'precio_periodo_gracia', 'precio_periodo_general')
    model = models.TarifaElectrica

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

#Listar las tarifas eléctricas de un usuario
class UserTarifasElectricas(generic.ListView):
    """
    Listado de las tarifas eléctricas personalizadas de un usuario en concreto.
    """

    model=models.TarifaElectrica
    template_name = "forecasting/user_tarifaelectrica_list.html"

    def get_queryset(self):
        try:
            self.tarifaelectrica_user=User.objects.get(username__iexact=self.kwargs.get("username"))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.tarifaelectrica_user.tarifaselectricas.all()

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        return context

#listado de los inmuebles, en general (probablemente me lo puedo cargar, porque sólo quiero listar por usuario)
# class TarifaElectricaList(SelectRelatedMixin, generic.ListView):
#     model=models.TarifaElectrica
#     select_related = ("user", )

#muestra una tarifa eléctrica
class TarifaElectricaDetail(SelectRelatedMixin, generic.DetailView):
    """
    Muestra de la información de una tarifa eléctrica personalizada  en concreto.
    """

    model = models.TarifaElectrica
    select_related = ("user",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact = self.kwargs.get("username"))

#modificar una tarifa eléctrica
class TarifaElectricaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modificación de una tarifa eléctrica personalizada.
    """

    model = models.TarifaElectrica
    fields=['nombre', 'hora_ini_uno', 'duracion_uno', 'precio_uno', 'hora_ini_dos', 'duracion_dos', 'precio_dos']
    template_name_suffix = '_form_update'

#eliminar una tarifa eléctrica
class DeleteTarifaElectrica(LoginRequiredMixin, DeleteView):
    """
    Eliminación de una tarifa eléctrica personalizada.
    """

    model = models.TarifaElectrica
    success_url = reverse_lazy('home')

#eliminar
# TARIFA MERCADO REGULADO - histórico subido por el usuario
#Crear/subir un histórico de tarifas del Mercado Regulado
class CreateTarifaMercadoRegulado(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('fichero_precios',)
    model = models.TarifaMercadoRegulado

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

#eliminar
#Listar las tarifas eléctricas de un usuario
class UserTarifasMercadoRegulado(generic.ListView):
    model=models.TarifaMercadoRegulado
    template_name = "forecasting/user_tarifamercadoregulado_list.html"

    def get_queryset(self):
        try:
            self.tarifamercadoregulado_user=User.objects.get(username__iexact=self.kwargs.get("username"))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.tarifamercadoregulado_user.tarifasmercadoregulado.all()

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        return context

#eliminar
#Muetra una Tarifa del Mercado Regulado
class TarifaMercadoReguladoDetail(SelectRelatedMixin, generic.DetailView):
    model = models.TarifaMercadoRegulado
    select_related = ("user",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact = self.kwargs.get("username"))

#modificar una tarifa eléctrica
# class TarifaMercadoReguladoUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.TarifaElectrica
#     fields=['fichero_precios']
#     template_name_suffix = '_form_update'

#eliminar
#Elimina una tarifa del mercado regulado
class DeleteTarifaMercadoRegulado(LoginRequiredMixin, DeleteView):
    model = models.TarifaMercadoRegulado
    success_url = reverse_lazy('home')


# # HISTÓRICO MERCADO REGULADO
# #ver un histórico
# class HistoricoMercadoReguladoDetail(SelectRelatedMixin, generic.DetailView):
#     model=models.HistoricoMercadoRegulado
#     # select_related = ("user",)
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         return queryset.filter(id__iexact=self.kwargs.get("pk"))
#
#     def get_context_data(self, **kwargs):
#         if (self.kwargs.get('yearS') and self.kwargs.get('monthS') and self.kwargs.get('dayS') and self.kwargs.get('yearF') and self.kwargs.get('monthF') and self.kwargs.get('dayF')):
#             #Me viene fecha de inicio y de final
#             principioYear = self.kwargs['yearS']
#             principioMonth = self.kwargs['monthS']
#             principioDay = self.kwargs['dayS']
#             principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
#             principio = principio.isoformat('T')
#             finalYear = self.kwargs['yearF']
#             finalMonth = self.kwargs['monthF']
#             finalDay = self.kwargs['dayF']
#             final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
#             final = final.isoformat('T')
#         elif (self.kwargs.get('yearS') and self.kwargs.get('monthS') and self.kwargs.get('dayS')):
#             #Me viene sólo un día
#             principioYear = self.kwargs['yearS']
#             principioMonth = self.kwargs['monthS']
#             principioDay = self.kwargs['dayS']
#             principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
#             principio = principio.isoformat('T')
#             final = datetime(int(principioYear), int(principioMonth), int(principioDay), 1, 0, 0)
#             final += timedelta(days=1)
#             final = final.isoformat('T')
#         else:
#             #No me viene fecha
#             ahora = datetime.now().__format__('%Y-%m-%d')
#             principio = ahora + 'T02:00:00'
#             finalYear = datetime.now().__format__('%Y')
#             finalMonth = datetime.now().__format__('%m')
#             finalDay = datetime.now().__format__('%d')
#             final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
#             final += timedelta(days=1)
#             final = final.isoformat('T')
#
#         context = super(HistoricoMercadoReguladoDetail, self).get_context_data(**kwargs)
#
#         hMR=models.HistoricoMercadoRegulado.objects.all()
#         precios = pd.read_csv(hMR.precios_luz)
#
#         context['grafico_precio'] = plots.chart_precios_pvpc(principio, final)
#         return context





#eliminar
# CONSUMOS
class ConsumoList(SelectRelatedMixin, generic.ListView):
    model = models.Consumo
    select_related = ("user",)

#eliminar
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

#eliminar
class ConsumoDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Consumo
    select_related = ("user",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact = self.kwargs.get("username"))

#eliminar
class CreateConsumo(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('titulo', 'fichero_consumo')
    model = models.Consumo

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

#eliminar
class DeleteConsumo(LoginRequiredMixin, DeleteView):
    model = models.Consumo
    success_url = reverse_lazy('forecasting:all')




#eliminar
# MODELOS DE PREDICCIÓN
class ModeloPredList(SelectRelatedMixin, generic.ListView):
    model = models.ModeloPred
    #select_related = ("consumo_origen",)
    select_related = ("user", )

#eliminar
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

#eliminar
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

#eliminar
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

#eliminar
class DeleteModeloPred(LoginRequiredMixin, DeleteView):
    model = models.ModeloPred
    success_url = reverse_lazy('forecasting:all_MP')


#eliminar
# PREDICCIONES
class PrediccionList(SelectRelatedMixin, generic.ListView):
    model = models.Prediccion
    select_related = ("user", )

#eliminar
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

#eliminar
class PrediccionDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Prediccion
    select_related = ("created_by",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by__username__iexact = self.kwargs.get("username"))

#eliminar
class CreatePrediccion(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('titulo', 'modelopred_origen')
    model = models.Prediccion

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        form.instance.created_by = self.request.user
        self.object.save()
        return super().form_valid(form)

#eliminar
class DeletePrediccion(LoginRequiredMixin, DeleteView):
    model = models.Prediccion
    success_url = reverse_lazy('forecasting:all_PP')

#eliminar
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

    # """
    # # Abro y preparo el dataframe
    # c_o = ModeloPred.objects.get(pk=pk).consumo_origen.fichero_consumo
    # df = pd.read_csv(c_o, delimiter=';', decimal=',')
    # ristra = pd.date_range(df['Fecha'][0], periods=len(df), freq='H')
    # df['Fecha'] = ristra
    # df = df.drop(['CUPS', 'Hora', 'Metodo_obtencion'], axis=1)
    # df.index = pd.to_datetime(df['Fecha'])
    # df = df.drop(['Fecha'], axis=1)
    # df.index.freq = 'h'
    #
    # # Limpio los datos
    # filt_df = df.loc[:, 'Consumo_kWh']
    # low = .05
    # high = .95
    # quant_df_low = filt_df.quantile(low)
    # quant_df_high = filt_df.quantile(high)
    #
    # for index, row in df.iterrows():
    #     if row['Consumo_kWh'] < quant_df_low:
    #         row['Consumo_kWh'] = quant_df_low
    #     elif row['Consumo_kWh'] > quant_df_high:
    #         row['Consumo_kWh'] = quant_df_high
    #
    # tam_total = len(df)
    # tam_train = int(tam_total/0.8)
    # tam_test = tam_total-tam_train
    #
    # train = df.iloc[:tam_train]
    # test = df.iloc[tam_test:]
    #
    # model = SARIMAX(train['Consumo_kWh'], order=(1, 1, 1), seasonal_order=(2, 0, 3, 24))
    # results = model.fit()
    # """

    return True

    #User.ModeloPred.fichero_modeloPred = User.ModeloPred.consumo_origen
    #User.objects.get()



class PVPCView(TemplateView):
    """
    Representación de los precios del mercado regulado.
    """

    template_name = 'forecasting/pvpc_chart.html'

    # """
    # def get_queryset(self):
    #     recib = self.kwargs['yearS']
    #     print('ATENTO AQUI QUE VIENE:')
    #     print(recib)
    # """

    # """
    # def get(self, *args, **kwargs):
    #     print('Processing GET request in PVPCView')
    #     #resp = super().get(*args, **kwargs)
    #     if not self.kwargs['yearS'] or self.kwargs['monthS'] or self.kwargs['dayS'] or self.kwargs['yearF'] or self.kwargs['monthF'] or self.kwargs['dayF']:
    #         ahora = datetime.now().__format__('%Y-%m-%d')
    #         principio = ahora + 'T02:00:00'
    #         finalYear = datetime.now().__format__('%Y')
    #         finalMonth = datetime.now().__format__('%m')
    #         finalDay = datetime.now().__format__('%d')
    #         final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
    #         final += timedelta(days=1)
    #         final = final.isoformat('T')
    #     else:
    #         principioYear = self.kwargs['yearS']
    #         principioMonth = self.kwargs['monthS']
    #         principioDay = self.kwargs['dayS']
    #         principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
    #         principio = principio.isoformat('T')
    #         finalYear = self.kwargs['yearF']
    #         finalMonth = self.kwargs['monthF']
    #         finalDay = self.kwargs['dayF']
    #         final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
    #         final = final.isoformat('T')
    # """



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

        # """
        # if not (self.kwargs.get('yearS') or self.kwargs.get('monthS') or self.kwargs.get('dayS') or self.kwargs.get('yearF') or self.kwargs.get('monthF') or self.kwargs.get('dayF')):
        #     ahora = datetime.now().__format__('%Y-%m-%d')
        #     principio = ahora + 'T02:00:00'
        #     finalYear = datetime.now().__format__('%Y')
        #     finalMonth = datetime.now().__format__('%m')
        #     finalDay = datetime.now().__format__('%d')
        #     final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
        #     final += timedelta(days=1)
        #     final = final.isoformat('T')
        # else:
        #     principioYear = self.kwargs['yearS']
        #     principioMonth = self.kwargs['monthS']
        #     principioDay = self.kwargs['dayS']
        #     principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
        #     principio = principio.isoformat('T')
        #     finalYear = self.kwargs['yearF']
        #     finalMonth = self.kwargs['monthF']
        #     finalDay = self.kwargs['dayF']
        #     final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
        #     final = final.isoformat('T')
        # """


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
            # """
            # ahora = datetime.now().__format__('%Y-%m-%d')
            # principio = ahora + 'T02:00:00'
            # finalYear = datetime.now().__format__('%Y')
            # finalMonth = datetime.now().__format__('%m')
            # finalDay = datetime.now().__format__('%d')
            # final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            # final += timedelta(days=1)
            # final = final.isoformat('T')
            # """


            ahora = datetime.now().__format__('%Y-%m-%d')
            principio = ahora + 'T02:00:00'
            # """
            # final = datetime.date.today().__format__('%Y-%m-%d') + datetime.timedelta(days=1)
            # """
            finalYear = datetime.now().__format__('%Y')
            finalMonth = datetime.now().__format__('%m')
            finalDay = datetime.now().__format__('%d')
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final += timedelta(days=1)
            final = final.isoformat('T')
            # """
            # final = str(ahora)
            # final += timedelta(days=1)
            # final = datetime(final, 1, 0, 0)
            # final = final.isoformat('T')
            # """

            # """
            # principio = '2019-05-05T02:00:00'
            # final = '2019-05-06T01:00:00'
            # """


        context = super(PVPCView, self).get_context_data(**kwargs)
        context['grafico_precio'] = plots.chart_precios_pvpc(principio, final)
        return context


# Clase para ver el histórico de precios desde del .csv de histórico
class HistoricoMRView(TemplateView):
    """
    Representación de los precios del mercado regulado, a partir del histórico de precios del sistema.
    """

    template_name='forecasting/mr_chart.html'

    def get_context_data(self, **kwargs):

        if (self.kwargs.get('yearS') and self.kwargs.get('monthS') and self.kwargs.get('dayS') and self.kwargs.get('yearF') and self.kwargs.get('monthF') and self.kwargs.get('dayF')):
            #Me viene fecha de inicio y de final
            principioYear = self.kwargs['yearS']
            principioMonth = self.kwargs['monthS']
            principioDay = self.kwargs['dayS']
            principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
            # principio = principio.isoformat('T')
            finalYear = self.kwargs['yearF']
            finalMonth = self.kwargs['monthF']
            finalDay = self.kwargs['dayF']
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            # final = final.isoformat('T')

        elif (self.kwargs.get('yearS') and self.kwargs.get('monthS') and self.kwargs.get('dayS')):
            #Me viene sólo un día
            principioYear = self.kwargs['yearS']
            principioMonth = self.kwargs['monthS']
            principioDay = self.kwargs['dayS']
            principio = datetime(int(principioYear), int(principioMonth), int(principioDay), 2, 0, 0)
            # principio = principio.isoformat('T')
            final = datetime(int(principioYear), int(principioMonth), int(principioDay), 1, 0, 0)
            final += timedelta(days=1)
            # final = final.isoformat('T')

        else:
            #No me viene fecha
            ahora = datetime.now().__format__('%Y-%m-%d')
            # principio = ahora + 'T02:00:00'
            principio = ahora + ' 02:00:00'

            finalYear = datetime.now().__format__('%Y')
            finalMonth = datetime.now().__format__('%m')
            finalDay = datetime.now().__format__('%d')
            final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
            final += timedelta(days=1)
            # final = final.isoformat('T')

        context = super(HistoricoMRView, self).get_context_data(**kwargs)
        context['grafica_precio'] = representar_precios_mr(principio, final)
        return context



class InformacionSmartMeters(TemplateView):
    """
    Muestra de información recopilada acerca de los Smart Meters.
    """

    template_name = 'forecasting/info_smartmeters.html'

class InformacionFactura(TemplateView):
    """
    Muestra de la información recopilada acerca de la factura de la luz en España.
    """
    template_name = 'forecasting/info_factura.html'

class InformacionEnergiaSpain(TemplateView):
    """
    Muestra de la información recopilada acerca de la generación eléctrica en España.
    """
    template_name = 'forecasting/info_energia_spain.html'


class PruebaIndex(TemplateView):
    template_name = 'forecasting/aaaa.html'