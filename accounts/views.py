from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from . import forms


# Create your views here.
class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"

# Mostrar la información de cuenta del usuario
class PerfilUsuario(TemplateView):
    template_name = 'accounts/perfil_usuario.html'