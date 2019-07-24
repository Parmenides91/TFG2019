"""
"""

from django.urls import path
from . import views

from django.conf import settings
from .models import HistoricoMercadoRegulado

app_name='forecasting'

urlpatterns = [
    # path('', views.ConsumoList.as_view(), name="all"),
    path("new/", views.CreateConsumo.as_view(), name="create"),
    path("by/<username>/", views.UserConsumos.as_view(), name="for_user"),
    path("by/<username>/<int:pk>/", views.ConsumoDetail.as_view(), name="single"),
    path("delete/<int:pk>/", views.DeleteConsumo.as_view(), name="delete"),
    path('modelos/', views.ModeloPredList.as_view(), name="all_MP"),
    path("newMP/", views.CreateModeloPred.as_view(), name="create_MP"),
    path("by/<username>/modelos/", views.UserModelosPred.as_view(), name="for_user_MP"),
    path("by/<username>/modelos/<int:pk>/", views.ModeloPredDetail.as_view(), name="single_MP"),
    path("modelos/delete/<int:pk>/", views.DeleteModeloPred.as_view(), name="delete_MP"),
    path('predicciones/', views.PrediccionList.as_view(), name="all_PP"),
    path("newPP/", views.CreatePrediccion.as_view(), name="create_PP"),
    path("by/<username>/predicciones/", views.UserPredicciones.as_view(), name="for_user_PP"),
    path("by/<username>/predicciones/<int:pk>/", views.PrediccionDetail.as_view(), name="single_PP"),
    path("predicciones/delete/<int:pk>/", views.DeletePrediccion.as_view(), name="delete_PP"),
    path("pvpc/", views.PVPCView.as_view(), name = "pvpc_precios"),
    path("pvpc/<int:yearS>/<int:monthS>/<int:dayS>/<int:yearF>/<int:monthF>/<int:dayF>/", views.PVPCView.as_view(), name ="pvpc_precios"),
    path("pvpc/<int:yearS>/<int:monthS>/<int:dayS>/", views.PVPCView.as_view(), name ="pvpc_precios"),
    path("pvpc/<int:yearS>-<int:monthS>-<int:dayS>/", views.PVPCView.as_view(), name ="pvpc_precios"),
    path("crear_fic_mod/<int:pk>", views.crear_fic_mod, name='crear_fic_mod'),
    #path("by/<username>/consumos/plot/<int:pk>/", views.ConsumoPlotDetail.as_view(), name="single_plot_C"),
    path('informacion_smartmeters/', views.InformacionSmartMeters.as_view(), name="infoS"),
    path('informacion_factura/', views.InformacionFactura.as_view(), name="infoF"),
    path('informacion_energia/', views.InformacionEnergiaSpain.as_view(), name="infoES"),
    #direcciones para inmuebles
    path('by/<username>/inmueble/', views.UserInmuebles.as_view(), name='for_user_inmuebles'),
    path('by/<username>/inmueble/new/', views.CreateInmueble.as_view(), name='create_inmueble'),
    path('by/<username>/inmueble/<int:pk>/', views.InmuebleDetail.as_view(), name='single_inmueble'),
    path('by/<username>/inmueble/edit/<int:pk>/', views.InmuebleUpdateView.as_view(), name='edit_inmueble'),
    path('by/<username>/inmueble/delete/<int:pk>/', views.DeleteInmueble.as_view(), name="delete_inmueble"),
    #direcciones para consumos parciales
    path('by/<username>/inmueble/new_consumo_parcial/', views.CreateConsumoParcial.as_view(), name='create_consumoparcial'),
    #direcciones para ver predicciones
    #path('by/<username>/inmueble/<int:pkI>/prediccion/<int:pkP>', views.PrediccionConsumoDetail.as_view(), name='single_prediccionconsumo'),
    path('prediccion/<int:pk>', views.PrediccionConsumoDetail.as_view(), name='single_prediccionconsumo'),
    path('prediccion/delete/<int:pk>', views.DeletePrediccionConsumo.as_view(), name='delete_prediccionconsumo'),
    # #direcciones para histórico mercado regulado
    # path('mercado-regulado/<int:pk>', views.HistoricoMercadoReguladoDetail.as_view(), name='single_historicomercadoregulado'),
    # direcciones para las tarifas eléctricas
    path('by/<username>/tarifa/', views.UserTarifasElectricas.as_view(), name='for_user_tarifaselectricas'),
    path('by/<username>/tarifa/new_tarifa_electrica/', views.CreateTarifaElectrica.as_view(), name='create_tarifaelectrica'),
    path('by/<username>/tarifa/<int:pk>/', views.TarifaElectricaDetail.as_view(), name='single_tarifaelectrica'),
    path('by/<username>/tarifa/edit/<int:pk>/', views.TarifaElectricaUpdateView.as_view(), name='edit_tarifaelectrica'),
    path('by/<username>/tarifa/delete/<int:pk>/', views.DeleteTarifaElectrica.as_view(), name="delete_tarifaelectrica"),
    # direcciones para las tarifas del mercado regulado
    path('by/<username>/regulado/', views.UserTarifasMercadoRegulado.as_view(), name='for_user_tarifasmercadoregulado'),
    path('by/<username>/regulado/new_tarifa_mr/', views.CreateTarifaMercadoRegulado.as_view(), name='create_tarifamercadoregulado'),
    path('by/<username>/regulado/<int:pk>/', views.TarifaMercadoReguladoDetail.as_view(), name='single_tarifamercadoregulado'),
    # path('by/<username>/regulado/edit/<int:pk>/', views.TarifaMercadoReguladoUpdateView.as_view(), name='edit_tarifamercadoregulado'),
    path('by/<username>/regulado/delete/<int:pk>/', views.DeleteTarifaMercadoRegulado.as_view(), name="delete_tarifamercadoregulado"),
    # Prueba de la Plantilla con un Index
    path('prueba_index/', views.PruebaIndex.as_view(), name="pruebaIndex"),
    # histórico de precios del mercado regulado
    path('historico_mr/', views.HistoricoMRView.as_view(), name = "mr_precios"),
    path("historico_mr/<int:yearS>/<int:monthS>/<int:dayS>/<int:yearF>/<int:monthF>/<int:dayF>/", views.HistoricoMRView.as_view(), name ="mr_precios"),
    path("historico_mr/<int:yearS>/<int:monthS>/<int:dayS>/", views.HistoricoMRView.as_view(), name ="mr_precios"),
    path("historico_mr/<int:yearS>-<int:monthS>-<int:dayS>/", views.HistoricoMRView.as_view(), name ="mr_precios"),
]

# El histórico de precios de la luz:
historicoSys = HistoricoMercadoRegulado.objects.create(ruta_fichero=settings.MEDIA_DIR+'\\historicoMR\\HistoricoPreciosMR.csv')
