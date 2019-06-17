from django import forms
from . import models

import pandas as pd
from .funciones_basicas import limpiarCSV


#formulario para la creación de un nuevo inmueble
class InmuebleForm(forms.ModelForm):
    class Meta():
        fields=('nombre','descripcion', 'consumo_inmueble')
        model=models.Inmueble
        filename = forms.FileField

    # def clean(self):
    #     cleaned_data=pd.read_csv(self.cleaned_data.get('filename').file, delimiter=';', decimal=',')
    #     cleaned_data=limpiarCSV(cleaned_data)
    #     return cleaned_data

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


#formulario para crear un consumo parcial de un inmueble
class ConsumoParcialForm(forms.ModelForm):
    class Meta():
        fields=('inmueble_asociado','fichero_consumo_parcial')
        model=models.ConsumoParcial

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

#formulario para crear un modelo a partir del consumo de un inmueble
class ModeloConsumoForm(forms.ModelForm):
    class Meta():
        fields=('inmueble_origen','fichero_modelo_inmueble')
        model=models.ModeloConsumo

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


#formulario para la creación de una nueva tarifa eléctrica
class TarifaElectricaForm(forms.ModelForm):
    class Meta():
        fields=('nombre', 'hora_ini_periodo_gracia', 'hora_fin_periodo_gracia', 'precio_periodo_gracia', 'precio_periodo_general')
        model=models.TarifaElectrica

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

#formulario para la creación de una nueva tarifa del mercado regulado
class TarifaMercadoReguladoForm(forms.ModelForm):
    class Meta():
        fields=('fichero_precios',)
        model=models.TarifaMercadoRegulado

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class ConsumoForm(forms.ModelForm):
    class Meta():
        fields = ("titulo", "fichero_consumo")
        model = models.Consumo

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class ModeloPredForm(forms.ModelForm):
    class Meta():
        fields = ("titulo", "consumo_origen")
        model = models.ModeloPred

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

class PrediccionForm(forms.ModelForm):
    class Meta():
        fields = ("titulo", "modelopred_origen")
        model = models.Prediccion

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

"""
class DateForm(forms.Form):
    date = forms.DateField(input_formats=['%d/%m/%Y'])
"""