import os, sys, django
# django独立脚本
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #把manage.py所在目录添加到系统目录  
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings' #设置setting文件  
django.setup()#初始化Django环境

import time
import exifread
import re
import requests
import json
import tkinter as tk
from tkinter import filedialog

from map.models import Photo

__author__ = 'RuanMing'

'''
代码功能：
1.读取所有图片文件的exif信息
2.提取图片中的经纬度，将度、分、秒转换为小数形式
3.利用百度地图API接口将经纬度转换成地址形
''' 

__n=0  # 读取的文件个数
__ni=0 # 照片的个数
__ng=0 # 存入数据库的个数

# 创建photo模型对象
__photo = None

__photoList = []

def app_run():
    root = tk.Tk()
    root.withdraw()

    foldpath = filedialog.askdirectory()
    if foldpath.strip() == '':
        return 
    
    get_pic_GPS(foldpath)
    try:
        Photo.objects.bulk_create(__photoList)
    except django.db.utils.IntegrityError as e:
        print(e.values)
    print('共遍历%s个文件，其中读取%s张照片，并存入数据库%s张照片。' % (__n,__ni,__ng))

# 遍历文件夹及子文件夹中的所有图片,逐个文件读取exif信息
def get_pic_GPS(pic_dir):
    global __n,__ni, __ng, __photo,__photoList
    items = os.listdir(pic_dir)
    for item in items:
        path = os.path.join(pic_dir, item)
        if os.path.isdir(path):
            get_pic_GPS(path)
        else:
            __n+=1
            suffix = os.path.splitext(item)[1]
            if(suffix=='.jpg' or suffix=='.tif' or suffix=='.jpeg' or suffix=='.JPG' or suffix=='.JPEG' or suffix=='.TIF'):
                __ni += 1
                if Photo.objects.filter(file_path=path):
                    continue
                __photo = Photo()
                __photo.file_name = item
                print(item)
                __photo.file_path = path
                print(path)
                imageread(path)
                if __photo.latitude == None or __photo.longitude == None:
                    continue
                __ng += 1
                __photoList.append(__photo)
                print('+++++++++++++++++++++++')

# 将经纬度转换为小数形式
def convert_to_decimal(*gps):
    # 度
    if '/' in gps[0]:
        deg = gps[0].split('/')
        if deg[0] == '0' or deg[1] == '0':
            gps_d = 0
        else:
            gps_d = float(deg[0]) / float(deg[1])
    else:
        gps_d = float(gps[0])
    # 分
    if '/' in gps[1]:
        minu = gps[1].split('/')
        if minu[0] == '0' or minu[1] == '0':
            gps_m = 0
        else:
            gps_m = (float(minu[0]) / float(minu[1])) / 60
    else:
        gps_m = float(gps[1]) / 60
    # 秒
    if '/' in gps[2]:
        sec = gps[2].split('/')
        if sec[0] == '0' or sec[1] == '0':
            gps_s = 0
        else:
            gps_s = (float(sec[0]) / float(sec[1])) / 3600
    else:
        gps_s = float(gps[2]) / 3600

    decimal_gps = gps_d + gps_m + gps_s
    # 如果是南半球或是西半球
    if gps[3] == 'W' or gps[3] == 'S' or gps[3] == "83" or gps[3] == "87":
        return str(decimal_gps * -1)
    else:
        return str(decimal_gps)

# 判断时间先后
def compare_time(time1,time2):
    if time1 <= time2:
        return time1
    else:
        return time2

# 读取图片的经纬度和拍摄时间
def imageread(path):
    global __photo

    f = open(path, 'rb')
    GPS = {}
    #Data = ""
    try:
        tags = exifread.process_file(f)
        # 读取创建时间和修改时间
        mtime = os.path.getmtime(path)
        ctime = os.path.getctime(path)
        # 确定较早时间
        ftime = compare_time(mtime,ctime)
        # print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ftime)))
    except:
        return
    # print(tags)
    '''
    for tag in tags:               
        print(tag,":",tags[tag])
    '''

    # 南北半球标识
    if 'GPS GPSLatitudeRef' in tags:
        GPS['GPSLatitudeRef'] = str(tags['GPS GPSLatitudeRef'])
        # print(GPS['GPSLatitudeRef'])
    else:
        GPS['GPSLatitudeRef'] = 'N'  # 缺省设置为北半球

    # 东西半球标识
    if 'GPS GPSLongitudeRef' in tags:
        GPS['GPSLongitudeRef'] = str(tags['GPS GPSLongitudeRef'])
        # print(GPS['GPSLongitudeRef'])
    else:
        GPS['GPSLongitudeRef'] = 'E'  # 缺省设置为东半球

    # 海拔高度标识
    """ if 'GPS GPSAltitudeRef' in tags:
        GPS['GPSAltitudeRef'] = str(tags['GPS GPSAltitudeRef']) """

    # 获取纬度
    if 'GPS GPSLatitude' in tags:
        lat = str(tags['GPS GPSLatitude'])
        # 处理无效值
        if lat == '[0, 0, 0]' or lat == '[0/0, 0/0, 0/0]':
            return

        deg, minu, sec = [x.replace(' ', '') for x in lat[1:-1].split(',')]
        # 将纬度转换为小数形式
        GPS['GPSLatitude'] = convert_to_decimal(deg, minu, sec, GPS['GPSLatitudeRef'])
        __photo.latitude = GPS['GPSLatitude']
        print(GPS['GPSLatitude'])

    # 获取经度
    if 'GPS GPSLongitude' in tags:
        lng = str(tags['GPS GPSLongitude'])
        # print(lng)

        # 处理无效值
        if lng == '[0, 0, 0]' or lng == '[0/0, 0/0, 0/0]':
            return

        deg, minu, sec = [x.replace(' ', '') for x in lng[1:-1].split(',')]
        # 将经度转换为小数形式
        GPS['GPSLongitude'] = convert_to_decimal(deg, minu, sec, GPS['GPSLongitudeRef'])  # 对特殊的经纬度格式进行处理
        __photo.longitude = GPS['GPSLongitude']
        print(GPS['GPSLongitude'])

    # 获取海拔高度
    """ if 'GPS GPSAltitude' in tags:
        GPS['GPSAltitude'] = str(tags["GPS GPSAltitude"]) """

    # 获取图片拍摄时间
    if 'Image DateTime' in tags:
        str_t = str(tags["Image DateTime"])
        if str_t == '':
            GPS["DateTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ftime))
        else:
            tmp_t = time.mktime(time.strptime(str_t, '%Y:%m:%d %H:%M:%S'))
            GPS["DateTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(compare_time(tmp_t, ftime)))
    elif "EXIF DateTimeOriginal" in tags:
        str_t = str(tags["EXIF DateTimeOriginal"])
        if str_t == '':
            GPS["DateTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ftime))
        else:
            tmp_t = time.mktime(time.strptime(str_t, '%Y:%m:%d %H:%M:%S'))
            GPS["DateTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(compare_time(tmp_t, ftime)))
    else:
        GPS["DateTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ftime))
    __photo.create_date = GPS["DateTime"]
    print(GPS["DateTime"])

    # 获取图片相机类型
    if 'Image Make' in tags:
        GPS["Image Make"] = str(tags['Image Make'])
        __photo.image_make = GPS["Image Make"]
        print('照相机制造商：', GPS["Image Make"])
    if 'Image Model' in tags:
        GPS["Image Model"] = str(tags['Image Model'])
        __photo.image_model = GPS["Image Model"]
        print('照相机型号：', GPS['Image Model'])

    """ if 'Image ExifImageWidth' in tags:
            print('照片尺寸：', tags['EXIF ExifImageWidth'],tags['EXIF ExifImageLength']) """

    if 'GPSLatitude' in GPS:
        # 将经纬度转换为地址
        convert_gps_to_address(GPS)
        #convert_gps_to_address_gaode(GPS)


#利用高德逆地理编码服务,无法提供全球服务
def convert_gps_to_address_gaode(GPS):
    global __photo
    secret_key = '7d7e331cacafeb69fc1c9339aa14d1b5'  # 密钥
    locations = '%s,%s' % (GPS['GPSLongitude'], GPS['GPSLatitude'])
    # 坐标转换
    gaode_convert_coord = 'https://restapi.amap.com/v3/assistant/coordinate/convert?locations=%s&coordsys=gps&output=json&key=%s' % (locations,secret_key)
    convert_content = requests.get(gaode_convert_coord).text
    convert_content_json = json.loads(convert_content)
    if convert_content_json['status'] == '1':
        locations = convert_content_json['locations']
    # 逆地理编码
    gaode_map_api = 'https://restapi.amap.com/v3/geocode/regeo?output=json&location=%s&key=%s&radius=1000&extensions=all' % (locations, secret_key)     
    content = requests.get(gaode_map_api).text
    gps_address = json.loads(content)
    if gps_address['status'] == '1':
        # 结构化的地址
        #print(gps_address)
        formatted_address = gps_address["regeocode"]["formatted_address"]
        
        __photo.address = formatted_address
        print(formatted_address)

# 利用百度全球逆地理编码服务（Geocoder）Web API接口服务将经纬转换为位置信息
def convert_gps_to_address(GPS):
    global __photo
    secret_key = 'jhErV0ZxK1t79Ug2E4PtCle3w4gkcA2z'  # 百度密钥
    lat, lng = GPS['GPSLatitude'], GPS['GPSLongitude']
    # 注意coordtype为wgs84ll(GPS经纬度),否则定位会出现偏差
    baidu_map_api = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=%s&output=json&coordtype=wgs84ll&location=%s,%s' % (secret_key, lat, lng)     
    content = requests.get(baidu_map_api).text
    gps_address = json.loads(content)
    if gps_address['status'] != 0:
        return
    # 结构化的地址
    #print(gps_address)
    formatted_address = gps_address["result"]["formatted_address"]
    # 国家（若需访问境外POI，需申请逆地理编码境外POI服务权限）
    #country = gps_address["result"]["addressComponent"]["country"]
    # 省
    #province = gps_address["result"]["addressComponent"]["province"]
    # 城市
    #city = gps_address["result"]["addressComponent"]["city"]
    # 区
    #district = gps_address["result"]["addressComponent"]["district"]
    # 语义化地址描述
    #sematic_description = gps_address["result"]["sematic_description"]
    # 将转换后的信息写入文件
    """ with open("gps_address.csv", "a+") as csv:
        csv.write(GPS[
                      "DateTime"] + "|" + formatted_address + "|" + country + "|" + province + "|" + city + "|" + district + "|" + sematic_description + "\n") """
    __photo.address = formatted_address
    print(formatted_address)


if __name__ == "__main__":
    app_run()
