from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from CountActApp import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.inicio, name='homepage'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('login/interno/', views.login_interno, name='login_interno'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('dashboard/usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    path('dashboard/gestor/', views.dashboard_gestor, name='dashboard_gestor'),
    path('dashboard/analista/', views.dashboard_analista, name='dashboard_analista'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/admin/crear-gestor/', views.crear_gestor, name='crear_gestor'),
    path('dashboard/admin/crear-analista/', views.crear_analista, name='crear_analista'),
    
    # PQRS - Rutas
    path('pqrs/crear/', views.crear_pqrs, name='crear_pqrs'),
    path('pqrs/<int:pqrs_id>/detalle/', views.detalle_pqrs, name='detalle_pqrs'),
    path('pqrs/<int:pqrs_id>/asignar/', views.asignar_pqrs, name='asignar_pqrs'),
    path('pqrs/<int:pqrs_id>/actualizar-estado/', views.actualizar_estado_pqrs, name='actualizar_estado_pqrs'),
]
