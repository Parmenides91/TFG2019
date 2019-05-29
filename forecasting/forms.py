from django import forms
from . import models

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