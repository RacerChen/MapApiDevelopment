import json
import requests
from Keys import Baidu_AK
import pandas as pd


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
        :return:
        """
        url = 'https://api.map.baidu.com/traffic/v1/around?ak=%s&center=%s,%s&radius=%s' \
              '&coord_type_input=gcj02&coord_type_output=gcj02' % (self.AK, lat, lon, radius)
        json_content = self.requestUrlGetJson(url)
        print(json_content)

    def coord2placeInfo(self, lon, lat):
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
            print(business)
            print(district, street, street_number, distance)


# Util BaiduHttpRequest to do coord transform
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


def get_traffic_around():
    bhr = BaiduHttpRequest()  # for util baidu api
    bhr.trafficInfoAroundAt('121.4675119', '31.2232067', '50')


if __name__ == '__main__':
    mbhr = BaiduHttpRequest()
    # lon, lat = hr.coordsTransform('121.3644257', '31.1040644', '1', '3')
    # print(lon, lat)

    # transform_df_wgs84_to_gcj02('shanghai_interpreter_highway_cross_wgs84.csv',
    #                             'shanghai_interpreter_highway_cross_gcj02.csv')

    # get_traffic_around()

    mbhr.coord2placeInfo('121.4629509', '31.2251191')
