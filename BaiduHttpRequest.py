import json
import requests
from Keys import Baidu_AK
import pandas as pd
import numpy as np


GS_coord_precision = 7


class BaiduHttpRequest:
    def __init__(self):
        self.AK = Baidu_AK

    @ staticmethod
    def requestUrlGetJson(url):
        """
        向url发送get请求，返回json格式数据
        :param url: get请求的url
        :return:
        """
        request = requests.get(url)
        str_content = str(request.content, 'utf-8')  # byte->str
        json_content = json.loads(str_content)  # str->json
        return json_content

    def coordsTransform(self, lon, lat, from_type, to_type):
        """
        用百度地图api进行坐标转换
        :param lon: 经度
        :param lat: 纬度
        :param from_type: 原坐标类型
        1：GPS标准坐标（wgs84）；
        2：搜狗地图坐标；
        3：火星坐标（gcj02），即高德地图、腾讯地图和MapABC等地图使用的坐标；
        4：3中列举的地图坐标对应的墨卡托平面坐标;
        5：百度地图采用的经纬度坐标（bd09ll）；
        6：百度地图采用的墨卡托平面坐标（bd09mc）;
        7：图吧地图坐标；
        8：51地图坐标；
        :param to_type: 目标坐标类型
        3：火星坐标（gcj02），即高德地图、腾讯地图及MapABC等地图使用的坐标；
        5：百度地图采用的经纬度坐标（bd09ll）；
        6：百度地图采用的墨卡托平面坐标（bd09mc）；
        :return: 转换后的经度, 转换后的纬度
        """
        url = 'https://api.map.baidu.com/geoconv/v1/?coords=%s,%s&from=%s&to=%s&ak=%s'\
                      % (lon, lat, from_type, to_type, self.AK)
        json_content = self.requestUrlGetJson(url)
        if json_content['status'] == 0:  # 成功返回
            return json_content['result'][0]['x'], json_content['result'][0]['y']
        else:
            return None, None

    def trafficInfoAroundAt(self, lon, lat, radius):
        """
        获取中心经纬坐标(gcj02)周围半径多少内的交通状况
        :param lon: 经度
        :param lat: 纬度
        :param radius: 半径，单位：米
        :return: 交通状况状态数，交通状况描述，相关的道路名称
        0：未知路况
        1：畅通
        2：缓行
        3：拥堵
        4：严重拥堵
        """
        url = 'https://api.map.baidu.com/traffic/v1/around?ak=%s&center=%s,%s&radius=%s' \
              '&coord_type_input=gcj02&coord_type_output=gcj02' % (self.AK, lat, lon, radius)
        json_content = self.requestUrlGetJson(url)
        print(json_content)
        if json_content['status'] == 0:
            evaluation = json_content['evaluation']
            evaluation_status = evaluation['status']
            evaluation_status_desc = evaluation['status_desc']
            relates_roads = ''
            for road in json_content['road_traffic']:
                relates_roads += road['road_name']
                relates_roads += '.'
            return evaluation_status, evaluation_status_desc, relates_roads
        else:
            return '', '', ''

    def coord2placeInfo(self, lon, lat):
        """
        返回将经纬度地区的商圈、区划、街道、街道号以及距离道路的距离信息list
        :param lon: gcj02经度
        :param lat: gcj02纬度
        :return:
        """
        url = 'https://api.map.baidu.com/reverse_geocoding/v3/?ak=%s&output=json&coordtype=gcj02&location=%s,%s' % \
              (self.AK, lat, lon)
        json_content = self.requestUrlGetJson(url)
        print(json_content)
        if json_content['status'] == 0:
            results = json_content['result']
            business = results['business']
            addressComponent = results['addressComponent']
            district = addressComponent['district']
            street = addressComponent['street']
            street_number = addressComponent['street_number']
            distance = addressComponent['distance']  # distance from road in meter
            business = business.replace(',', '.')
            print([business, district, street, street_number, distance])
            return [business, district, street, street_number, distance]


# Step1: Util BaiduHttpRequest to do coord transform
def transform_df_wgs84_to_gcj02(wgs84_df_csv, gcj02_df_csv):
    """
    transform df of wgs84 to gcj02
    :param wgs84_df_csv: wgs84 df.csv filename
    :param gcj02_df_csv: gcj02 df.csv filename
    :return:
    """
    bhr = BaiduHttpRequest()  # for util baidu api

    wgs84_df = pd.read_csv(wgs84_df_csv)
    gcj02_df = pd.DataFrame(columns=['id', 'lon', 'lat'])
    for i in range(len(wgs84_df)):
        print(f'Progress: {i}/{len(wgs84_df)}...')
        wgs84_lon = wgs84_df.iloc[i]['lon']
        wgs84_lat = wgs84_df.iloc[i]['lat']
        gcj02_lon, gcj02_lat = bhr.coordsTransform(wgs84_lon, wgs84_lat, '1', '3')
        gcj02_df = gcj02_df.append({'id': str(int(wgs84_df.iloc[i]['id'])), 'lon': round(gcj02_lon, GS_coord_precision),
                                    'lat': round(gcj02_lat, GS_coord_precision)}, ignore_index=True)
    print(wgs84_df)
    print(gcj02_df)
    gcj02_df.to_csv(gcj02_df_csv, index=False)


# Step2: 坐标转换
def get_all_local_info(highway_cross_csv):
    """
    将路口信息转换为地理详细信息
    :param highway_cross_csv: 路口信息csv文件
    :return:
    """
    all_local_info_df = pd.DataFrame(columns=['id', 'lon', 'lat', 'business',
                                              'district', 'street', 'street_number', 'distance'])
    bhr = BaiduHttpRequest()  # for util baidu api
    df = pd.read_csv(highway_cross_csv)
    for i in range(len(df)):
        df_line = df.iloc[i]
        cur_local_info_list = bhr.coord2placeInfo(df_line['lon'], df_line['lat'])
        all_local_info_df = all_local_info_df.append({'id': df_line['id'], 'lon': df_line['lon'], 'lat': df_line['lat'],
                                                      'business': cur_local_info_list[0],
                                                      'district': cur_local_info_list[1],
                                                      'street': cur_local_info_list[2],
                                                      'street_number': cur_local_info_list[3],
                                                      'distance': cur_local_info_list[4]}, ignore_index=True)
    print(all_local_info_df)
    all_local_info_df.to_csv(highway_cross_csv.split('.')[0] + '_info.csv')


# Step3: 筛选出感兴趣区域
def get_key_area_df(highway_cross_info_csv, area_key):
    df = pd.read_csv(highway_cross_info_csv)
    df['aim'] = df['business'].str.contains(area_key).replace(np.nan, False)

    df_areas = df[df['aim']]
    del df_areas['aim']

    print(df_areas)
    df_areas.to_csv(highway_cross_info_csv.split('.')[0] + '_' + area_key + '.csv', index=False)


# Step4: 获取半径范围内的道路使用车辆实时情况
def get_traffic_around(area_csv, search_radius):
    bhr = BaiduHttpRequest()  # for util baidu api
    traffic_info_df = pd.DataFrame(columns=['id', 'lon', 'lat', 'status', 'status_desc', 'related_roads'])
    area_df = pd.read_csv(area_csv)
    for i in range(len(area_df)):
        # area_df.iloc[i]
        lid = area_df.iloc[i]['id']
        lon = area_df.iloc[i]['lon']
        lat = area_df.iloc[i]['lat']
        status, status_desc, related_roads = bhr.trafficInfoAroundAt(lon, lat, search_radius)
        traffic_info_df = traffic_info_df.append({'id': str(int(lid)), 'lon': lon, 'lat': lat,
                                                  'status': status, 'status_desc': status_desc,
                                                  'related_roads': related_roads}, ignore_index=True)
    traffic_info_df.to_csv(area_csv.split('.')[0] + '_r' + search_radius + '.csv', index=False)


if __name__ == '__main__':
    mbhr = BaiduHttpRequest()
    # lon, lat = hr.coordsTransform('121.3644257', '31.1040644', '1', '3')
    # print(lon, lat)

    # transform_df_wgs84_to_gcj02('shanghai_interpreter_highway_cross_wgs84.csv',
    #                             'shanghai_interpreter_highway_cross_gcj02.csv')

    # get_traffic_around()

    # mbhr.coord2placeInfo('121.4629509', '31.2251191')

    # get_all_local_info('shanghai_interpreter_highway_cross_gcj02.csv')
    # get_key_area_df('shanghai_interpreter_highway_cross_gcj02_info.csv', '安亭')
    get_traffic_around('shanghai_interpreter_highway_cross_gcj02_info_五角场.csv', '100')
