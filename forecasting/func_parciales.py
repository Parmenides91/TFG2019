#from . import models
from .models import ConsumoParcial, Inmueble

def obtener_consumos_asociados(clave_inmueble, clave_usuario):
    inmueble = Inmueble.objects().get(user=clave_usuario, pk=clave_inmueble)
    consumos_parciales = ConsumoParcial.objects().filter(fk=inmueble)

    """
    consumos_parciales.
    inmueble.consumo_inmueble = None
    inmueble.delete()
    """
    for consumo_parcial in consumos_parciales:
        pass
