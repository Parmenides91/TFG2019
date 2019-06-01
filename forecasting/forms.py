from django import forms
from . import models


#formulario para la creación de un nuevo inmueble
class InmuebleForm(forms.ModelForm):
    class Meta():
        fields=('nombre','descripcion','consumo_inmueble')
        model=models.Inmueble

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