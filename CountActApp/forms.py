from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Gestor, Analista, PQRS


class UsuarioRegistroForm(UserCreationForm):
    """Formulario para que clientes se registren como usuarios"""
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


class CrearGestorForm(UserCreationForm):
    """Formulario para crear un Gestor (uso exclusivo del Administrador)"""
    cargo = forms.CharField(
        max_length=100,
        required=False,
        label='Cargo',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Gestor de Ventas'})
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'tipoCedula',
            'documento',
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
            'documento': 'Documento',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Escribe una contraseña segura.'
        self.fields['password2'].help_text = 'Repite la contraseña para confirmar.'


class CrearAnalistaForm(UserCreationForm):
    """Formulario para crear un Analista (uso exclusivo del Administrador)"""
    especialidad = forms.CharField(
        max_length=100,
        required=False,
        label='Especialidad',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Análisis de Sistemas'})
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'tipoCedula',
            'documento',
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
            'documento': 'Documento',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Escribe una contraseña segura.'
        self.fields['password2'].help_text = 'Repite la contraseña para confirmar.'


class CrearPQRSForm(forms.ModelForm):
    """Formulario para que usuarios creen PQRS"""
    class Meta:
        model = PQRS
        fields = ['tipo', 'asunto', 'descripcion', 'archivo_adjunto']
        labels = {
            'tipo': 'Tipo de solicitud',
            'asunto': 'Asunto',
            'descripcion': 'Descripción detallada',
            'archivo_adjunto': 'Archivo adjunto (opcional)',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resumen breve'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Describe tu solicitud detalladamente'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control'}),
        }