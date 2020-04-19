from django.urls import path
from . import views

app_name = 'map'
urlpatterns = [
    path('foliummap', views.folium_map, name='foliummap'),
    path('', views.baidu_map, name='baidumap'),
]