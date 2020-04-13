from django.shortcuts import render
from django.http import HttpResponse

import folium

# Create your views here.


def index(request):
    m = folium.Map(
        location=[22.83, 108.33],
        zoom_start=12
    )
    folium.Marker(
        location=[22.83, 108.33],
        popup='<i>Hello,world</i>', 
        icon=folium.Icon(icon='green')
    ).add_to(m)

    m = m._repr_html_()  # updated
    context = {'my_map': m}

    return render(request, 'map/index.html', context)
