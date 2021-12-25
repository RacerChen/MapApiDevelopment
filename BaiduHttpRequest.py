import json
import requests
from Keys import Baidu_AK
import pandas as pd


class BaiduHttpRequest:
    def __init__(self):
        self.AK = Baidu_AK

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
        request = requests.get(url)
        str_content = str(request.content, 'utf-8')  # byte->str
        json_content = json.loads(str_content)  # str->json
        if json_content['status'] == 0:  # 成功返回
            return json_content['result'][0]['x'], json_content['result'][0]['y']
        else:
            return None, None


def transform_df_wgs84_to_gcj02(wgs84_df_csv, gcj02_df_csv):
    """
    transform df of wgs84 to gcj02
    :param wgs84_df_csv: wgs84 df.csv filename
    :param gcj02_df_csv: gcj02 df.csv filename
    :return:
    """
    bhr = BaiduHttpRequest()  # for util baidu api

    wgs84_df = pd.read_csv(wgs84_df_csv)
    gcj02_df = wgs84_df
    for i in range(len(wgs84_df)):
        print(f'Progress: {i}/{len(wgs84_df)}...')
        wgs84_lon = wgs84_df.iloc[i]['lon']
        wgs84_lat = wgs84_df.iloc[i]['lat']
        gcj02_lon, gcj02_lat = bhr.coordsTransform(wgs84_lon, wgs84_lat, '1', '3')
        gcj02_df.iloc[i]['lon'] = gcj02_lon
        gcj02_df.iloc[i]['lat'] = gcj02_lat
    print(wgs84_df)
    print(gcj02_df)


if __name__ == '__main__':
    # hr = BaiduHttpRequest()
    # lon, lat = hr.coordsTransform('121.3644257', '31.1040644', '1', '3')
    # print(lon, lat)
    transform_df_wgs84_to_gcj02('shanghai_interpreter_highway_cross_wgs84.csv',
                                'shanghai_interpreter_highway_cross_gcj02.csv')
