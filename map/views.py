from django.shortcuts import render
from django.http import HttpResponse
from .models import Photo

import folium, json, datetime

# Create your views here.


def folium_map(request):
    m = folium.Map(
        location=[22.83, 108.33],
        zoom_start=12
    )
    photos = Photo.objects.all()
    for photo in photos:
        folium.Marker(
            location=[photo.latitude, photo.longitude],
            popup='<i>'+photo.file_name+'</i>', 
            icon=folium.Icon(icon='green')
        ).add_to(m)

    m = m._repr_html_()  # updated
    context = {'my_map': m}

    return render(request, 'map/foliummap.html', context)

def baidu_map(request):
    photos = Photo.objects.all()
    photos_longitude = []
    photos_latitude = []
    photos_file_name = []
    photos_file_path = []
    photos_create_date = []
    photos_address = []
    for i in range(len(photos)):
        photos_longitude.append(photos[i].longitude)
        photos_latitude.append(photos[i].latitude)
        photos_file_name.append(photos[i].file_name)
        photos_file_path.append(photos[i].file_path)
        photos_create_date.append(photos[i].create_date)
        photos_address.append(photos[i].address)
    context = {
        'photos_longitude': json.dumps(photos_longitude),
        'photos_latitude': json.dumps(photos_latitude),
        'photos_file_name': json.dumps(photos_file_name),
        'photos_file_path': json.dumps(photos_file_path),
        'photos_create_date': json.dumps(photos_create_date, cls=DataEncoder),
        'photos_address': json.dumps(photos_address)
    }
    
    return render(request, 'map/baidumap.html', context)

class DataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return super().default(self, obj)

