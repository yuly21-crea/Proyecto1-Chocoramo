from django.shortcuts import render, redirect
from .forms import UsuarioRegistroForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Usuario, Gestor, Analista
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseForbidden


def inicio(request):
    return render(request, 'homepage.html')

#                       --------------------REGISTRO DE USUARIOS---------------------
def registro_usuario(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            form.save()  # guarda el usuario y hashea la contraseña
            return redirect('login')  # redirige al login (puedes cambiarlo)
    else:
        form = UsuarioRegistroForm()
    return render(request, 'registro.html', {'form': form})

#                       --------------------LOGIN DE USUARIOS---------------------

class UsuarioLoginView(LoginView):
    template_name = 'login.html'  # tu plantilla
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Solo permite login a usuarios con rol USUARIO"""
        user = form.get_user()
        if user.rol != 'USUARIO':
            messages.error(self.request, 'Acceso denegado. Este login es solo para usuarios. Usa el acceso interno si eres personal autorizado.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard_usuario')
    
def login_interno(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.rol in ['GESTOR', 'ANALISTA', 'ADMINISTRADOR']:
            login(request, user)
            if user.rol == 'GESTOR':
                return redirect('dashboard_gestor')
            elif user.rol == 'ANALISTA':
                return redirect('dashboard_analista')
            elif user.rol == 'ADMINISTRADOR':
                return redirect('dashboard_admin')
        else:
            messages.error(request, 'Acceso no permitido o credenciales incorrectas')
    return render(request, 'login_interno.html')



#                       --------------SEGMENTACIÓN DE DASHBOARDS---------------

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder aquí.")
        return _wrapped_view
    return decorator


# --- DASHBOARDS DE PRUEBA ---
@rol_requerido(['USUARIO'])
def dashboard_usuario(request):
    return render(request, 'dashboards/dashboard_usuario.html')


@rol_requerido(['GESTOR'])
def dashboard_gestor(request):
    return render(request, 'dashboards/dashboard_gestor.html')


@rol_requerido(['ANALISTA'])
def dashboard_analista(request):
    return render(request, 'dashboards/dashboard_analista.html')


@rol_requerido(['ADMINISTRADOR'])
def dashboard_admin(request):
    return render(request, 'dashboards/dashboard_admin.html')


# Alias para compatibilidad: dashboard_cliente -> dashboard_usuario
def dashboard_cliente(request):
    return dashboard_usuario(request)





# Ejemplo de creación de un Gestor al registrar un usuario con rol GESTOR
def crear_gestor(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        nuevo_usuario = Usuario.objects.create_user(
            username=username,
            password=password,
            rol='GESTOR'
        )
        Gestor.objects.create(usuario=nuevo_usuario)


def crear_analista(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        nuevo_usuario = Usuario.objects.create_user(
            username=username,
            password=password,
            rol='ANALISTA'
        )
        Analista.objects.create(usuario=nuevo_usuario)