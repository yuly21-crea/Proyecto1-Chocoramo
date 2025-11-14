from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class UsuarioRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'tipoCedula',
            'documento',
            'email',
            'telefono',
            'direccion',
            'password1',
            'password2',
        ]
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'tipoCedula': 'Tipo de cédula',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        help_texts = {
            'username': 'Elige un nombre de usuario único. Solo letras, números y símbolos permitidos.',
            'password1': 'Escribe una contraseña segura.',
            'password2': 'Repite la contraseña para confirmar.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Deshabilitar los help_texts por defecto de UserCreationForm
        self.fields['password1'].help_text = 'Escribe una contraseña segura.'
        self.fields['password2'].help_text = 'Repite la contraseña para confirmar.'
        self.fields['username'].help_text = 'Elige un nombre de usuario único. Solo letras, números y símbolos permitidos.'