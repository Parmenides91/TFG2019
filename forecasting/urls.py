from django.urls import path
from . import views

app_name='forecasting'

urlpatterns = [
    path('', views.ConsumoList.as_view(), name="all"),
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
    path("crear_fic_mod/<int:pk>", views.crear_fic_mod, name='crear_fic_mod'),
    #path("by/<username>/consumos/plot/<int:pk>/", views.ConsumoPlotDetail.as_view(), name="single_plot_C"),
    path('informacion_smartmeters/', views.InformacionSmartMeters.as_view(), name="infoS"),
    path('informacion_factura/', views.InformacionFactura.as_view(), name="infoF"),
    path('informacion_energia/', views.InformacionEnergiaSpain.as_view(), name="infoES"),
]
