from django.urls import path
from . import views

app_name = 'map'
urlpatterns = [
    path('', views.folium_map, name='foliummap'),
    path('baidumap', views.baidu_map, name='baidumap'),
]