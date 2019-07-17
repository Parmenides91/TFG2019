"""
.. module:: models
    :synopsis: Contiene la clase usuario que se necesita para el sistema. Emplea el usuario predefinido de Django.

.. moduleauthor:: Roberto Benéitez Vaquero


"""



from django.db import models
from django.contrib import auth
from django.utils import timezone

# Create your models here.
class User(auth.models.User, auth.models.PermissionsMixin):
    """
    Clase usuario, predefinida por Django.
    """

    def __str__(self):
        return "@{}".format(self.username)
