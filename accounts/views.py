"""
.. module:: views
    :synopsis: Contiene todas las vistas de la app accounts.

.. moduleauthor:: Roberto Benéitez Vaquero


"""


from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from . import forms


# Create your views here.
class SignUp(CreateView):
    """
    Registro de nuevos usuarios en el sistema.
    """

    form_class = forms.UserCreateForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"

# Mostrar la información de cuenta del usuario
class PerfilUsuario(TemplateView):
    """
    Muestra de los datos que se poseen en el sistema relativos al usuario.
    """

    template_name = 'accounts/perfil_usuario.html'