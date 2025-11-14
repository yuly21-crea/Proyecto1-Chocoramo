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
    path('login_interno/', views.login_interno, name='login_interno'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('dashboard/usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    path('dashboard/gestor/', views.dashboard_gestor, name='dashboard_gestor'),
    path('dashboard/analista/', views.dashboard_analista, name='dashboard_analista'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
]
