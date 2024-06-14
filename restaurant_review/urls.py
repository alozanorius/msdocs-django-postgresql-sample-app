from django.urls import path

from . import views

app_name = "restaurant_review"
urlpatterns = [
    path('', views.mirar_directorio, name='mirar_directorio'),
    path('descargar_confirmacion/', views.descargar_confirmacion, name='descargar_confirmacion'),
    path('descargar_excel/', views.descargar_excel, name='descargar_excel'),
]
