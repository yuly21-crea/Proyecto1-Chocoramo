from django.shortcuts import render, redirect, get_object_or_404
from .forms import UsuarioRegistroForm, CrearGestorForm, CrearAnalistaForm, CrearPQRSForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Usuario, Gestor, Analista, PQRS, HistorialEstadoPQRS
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q


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
    # Obtener todas las PQRS del usuario actual
    pqrs_lista = PQRS.objects.filter(cliente=request.user).order_by('-fecha_creacion')
    context = {
        'pqrs_lista': pqrs_lista,
    }
    return render(request, 'dashboards/dashboard_usuario.html', context)


@rol_requerido(['GESTOR'])
def dashboard_gestor(request):
    # Obtener todas las PQRS en estado ENVIADA (sin asignar a analista)
    pqrs_sin_asignar = PQRS.objects.filter(estado='ENVIADA').order_by('-fecha_creacion')
    pqrs_asignadas = PQRS.objects.filter(
        Q(estado='ASIGNADA') | Q(estado='EN_PROCESO')
    ).order_by('-fecha_creacion')
    
    context = {
        'pqrs_sin_asignar': pqrs_sin_asignar,
        'pqrs_asignadas': pqrs_asignadas,
    }
    return render(request, 'dashboards/dashboard_gestor.html', context)


@rol_requerido(['ANALISTA'])
def dashboard_analista(request):
    try:
        # Obtener el perfil de Analista del usuario actual
        analista = Analista.objects.get(usuario=request.user)
        # Obtener todas las PQRS asignadas a este analista
        pqrs_asignadas = PQRS.objects.filter(analista_asignado=analista).order_by('-fecha_creacion')
    except Analista.DoesNotExist:
        pqrs_asignadas = []
    
    context = {
        'pqrs_asignadas': pqrs_asignadas,
    }
    return render(request, 'dashboards/dashboard_analista.html', context)


@rol_requerido(['ADMINISTRADOR'])
def dashboard_admin(request):
    return render(request, 'dashboards/dashboard_admin.html')


# Alias para compatibilidad: dashboard_cliente -> dashboard_usuario
def dashboard_cliente(request):
    return dashboard_usuario(request)


# ===================== FUNCIONES PARA CREAR Y GESTIONAR PQRS =====================

@rol_requerido(['USUARIO'])
def crear_pqrs(request):
    """Vista para que el usuario cree una nueva PQRS"""
    if request.method == 'POST':
        form = CrearPQRSForm(request.POST, request.FILES)
        if form.is_valid():
            pqrs = form.save(commit=False)
            pqrs.cliente = request.user  # Asignar el usuario actual como cliente
            pqrs.estado = 'ENVIADA'  # Estado inicial
            pqrs.save()
            
            # Crear un registro en el historial
            HistorialEstadoPQRS.objects.create(
                pqrs=pqrs,
                estado_anterior='NUEVA',
                estado_nuevo='ENVIADA',
                cambiado_por=request.user
            )
            
            messages.success(request, 'Tu PQRS ha sido creada exitosamente.')
            return redirect('dashboard_usuario')
    else:
        form = CrearPQRSForm()
    
    return render(request, 'crear_pqrs.html', {'form': form})


@rol_requerido(['GESTOR'])
def asignar_pqrs(request, pqrs_id):
    """Vista para que el gestor asigne una PQRS a un analista"""
    pqrs = get_object_or_404(PQRS, id=pqrs_id)
    
    if request.method == 'POST':
        analista_id = request.POST.get('analista_id')
        if analista_id:
            try:
                analista = Analista.objects.get(id=analista_id)
                # Cambiar estado y asignar analista
                estado_anterior = pqrs.estado
                pqrs.analista_asignado = analista
                pqrs.estado = 'ASIGNADA'
                pqrs.save()
                
                # Registrar el cambio en el historial
                HistorialEstadoPQRS.objects.create(
                    pqrs=pqrs,
                    estado_anterior=estado_anterior,
                    estado_nuevo='ASIGNADA',
                    cambiado_por=request.user
                )
                
                messages.success(request, f'PQRS #{pqrs.id} asignada a {analista.usuario.first_name} {analista.usuario.last_name}.')
                return redirect('dashboard_gestor')
            except Analista.DoesNotExist:
                messages.error(request, 'El analista seleccionado no existe.')
    
    # Obtener lista de analistas activos
    analistas = Analista.objects.filter(activo=True)
    context = {
        'pqrs': pqrs,
        'analistas': analistas,
    }
    return render(request, 'asignar_pqrs.html', context)


@rol_requerido(['ANALISTA'])
def actualizar_estado_pqrs(request, pqrs_id):
    """Vista para que el analista actualice el estado de una PQRS"""
    pqrs = get_object_or_404(PQRS, id=pqrs_id)
    
    # Verificar que la PQRS está asignada a este analista
    try:
        analista = Analista.objects.get(usuario=request.user)
        if pqrs.analista_asignado != analista:
            return HttpResponseForbidden("No tienes permiso para actualizar esta PQRS.")
    except Analista.DoesNotExist:
        return HttpResponseForbidden("No eres un analista registrado.")
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(PQRS.ESTADO_CHOICES):
            estado_anterior = pqrs.estado
            pqrs.estado = nuevo_estado
            pqrs.save()
            
            # Registrar el cambio en el historial
            HistorialEstadoPQRS.objects.create(
                pqrs=pqrs,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                cambiado_por=request.user
            )
            
            messages.success(request, f'Estado de la PQRS #{pqrs.id} actualizado a {nuevo_estado}.')
            return redirect('dashboard_analista')
    
    context = {
        'pqrs': pqrs,
        'estados': PQRS.ESTADO_CHOICES,
    }
    return render(request, 'actualizar_estado_pqrs.html', context)


@rol_requerido(['USUARIO', 'GESTOR', 'ANALISTA', 'ADMINISTRADOR'])
def detalle_pqrs(request, pqrs_id):
    """Vista para ver el detalle de una PQRS"""
    pqrs = get_object_or_404(PQRS, id=pqrs_id)
    
    # Verificar que el usuario es el cliente o es personal autorizado
    if request.user != pqrs.cliente and request.user.rol == 'USUARIO':
        return HttpResponseForbidden("No tienes permiso para ver esta PQRS.")
    
    historial = pqrs.historial_estados.all().order_by('-fecha_cambio')
    
    context = {
        'pqrs': pqrs,
        'historial': historial,
    }
    return render(request, 'detalle_pqrs.html', context)





# Ejemplo de creación de un Gestor al registrar un usuario con rol GESTOR
@rol_requerido(['ADMINISTRADOR'])
def crear_gestor(request):
    if request.method == 'POST':
        form = CrearGestorForm(request.POST)
        if form.is_valid():
            # Crear el usuario con rol GESTOR
            usuario = form.save(commit=False)
            usuario.rol = 'GESTOR'
            usuario.save()
            
            # Crear el registro de Gestor asociado
            cargo = form.cleaned_data.get('cargo', '')
            Gestor.objects.create(usuario=usuario, cargo=cargo)
            
            messages.success(request, f'Gestor {usuario.username} creado exitosamente.')
            return redirect('dashboard_admin')
    else:
        form = CrearGestorForm()
    
    return render(request, 'crear_gestor.html', {'form': form})


@rol_requerido(['ADMINISTRADOR'])
def crear_analista(request):
    if request.method == 'POST':
        form = CrearAnalistaForm(request.POST)
        if form.is_valid():
            # Crear el usuario con rol ANALISTA
            usuario = form.save(commit=False)
            usuario.rol = 'ANALISTA'
            usuario.save()
            
            # Crear el registro de Analista asociado
            especialidad = form.cleaned_data.get('especialidad', '')
            Analista.objects.create(usuario=usuario, especialidad=especialidad)
            
            messages.success(request, f'Analista {usuario.username} creado exitosamente.')
            return redirect('dashboard_admin')
    else:
        form = CrearAnalistaForm()
    
    return render(request, 'crear_analista.html', {'form': form})