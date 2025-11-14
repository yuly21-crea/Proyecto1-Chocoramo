from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class Usuario(AbstractUser):
    tipoCedula = models.CharField(
        max_length=20,
        choices=[
            ('CC', 'Cédula de Ciudadanía'),
            ('TI', 'Tarjeta de Identidad'),
            ('CE', 'Cédula de Extranjería')
        ]
    )
    documento = models.IntegerField(unique=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=100)
    rol = models.CharField(
        max_length=20,
        choices=[
        ('USUARIO', 'Usuario'),
        ('GESTOR', 'Gestor'),
        ('ANALISTA', 'Analista'),
        ('ADMINISTRADOR', 'Administrador'),
    ],
        default='USUARIO')

    # puedes usar email como username si quieres:
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'tipoCedula', 'documento']

    def __str__(self):
        return self.email


# ---------------------------------------
# 1. GESTOR
# ---------------------------------------
class Gestor(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Gestor: {self.usuario.username}"


# ---------------------------------------
# 2. ANALISTA
# ---------------------------------------
class Analista(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Analista: {self.usuario.username}"


# ---------------------------------------
# 3. PQRS
# ---------------------------------------
class PQRS(models.Model):
    TIPO_CHOICES = [
        ('P', 'Petición'),
        ('Q', 'Queja'),
        ('R', 'Reclamo'),
        ('S', 'Sugerencia'),
    ]

    ESTADO_CHOICES = [
        ('ENVIADA', 'Enviada'),
        ('ASIGNADA', 'Asignada a Analista'),
        ('EN_PROCESO', 'En Proceso'),
        ('RESUELTA', 'Resuelta'),
        ('CERRADA', 'Cerrada'),
    ]

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pqrs_enviadas'
    )
    gestor_asignado = models.ForeignKey(
        Gestor, on_delete=models.SET_NULL, null=True, blank=True, related_name='pqrs_asignadas'
    )
    analista_asignado = models.ForeignKey(
        Analista, on_delete=models.SET_NULL, null=True, blank=True, related_name='pqrs_analizadas'
    )

    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ENVIADA')

    archivo_adjunto = models.FileField(upload_to='archivos_pqrs/', null=True, blank=True)

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.asunto} ({self.estado})"


# ---------------------------------------
# 4. RESPUESTA / REPORTE DEL ANALISTA
# ---------------------------------------
class RespuestaPQRS(models.Model):
    pqrs = models.OneToOneField(PQRS, on_delete=models.CASCADE, related_name='respuesta')
    analista = models.ForeignKey(Analista, on_delete=models.SET_NULL, null=True)
    contenido = models.TextField()
    fecha_respuesta = models.DateTimeField(default=timezone.now)
    archivo_reporte = models.FileField(upload_to='reportes_analistas/', null=True, blank=True)
    enviada_al_cliente = models.BooleanField(default=False)

    def __str__(self):
        return f"Respuesta a PQRS #{self.pqrs.id} por {self.analista}"


# ---------------------------------------
# 5. HISTORIAL DE ESTADOS
# ---------------------------------------
class HistorialEstadoPQRS(models.Model):
    pqrs = models.ForeignKey(PQRS, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    fecha_cambio = models.DateTimeField(default=timezone.now)
    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Cambio {self.estado_anterior} → {self.estado_nuevo} ({self.pqrs.id})"