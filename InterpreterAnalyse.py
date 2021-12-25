from xml.etree import ElementTree as ET
import pandas as pd
"""
Step1: generate interpreter file from OpenStreetMap:
Detail can be seen in: https://blog.csdn.net/weixin_40992982/article/details/100174266

Step2: Then use InterpreterAnalyse generate the highway cross info dataframe, now, the coordinate format is wgs84
"""


class InterpreterAnalyse:
    def __init__(self, interpreter_filename):
        self.nodes_count = -1
        self.interpreter_filename = interpreter_filename
        xml_tree = ET.parse(interpreter_filename)
        self.interpreter_root = xml_tree.getroot()
        self.highway_cross_df = pd.DataFrame(columns=['id', 'lon', 'lat'])

    def iterAllNodes(self):
        temp_count = 0
        nodes = self.interpreter_root.findall('node')
        for node in nodes:
            temp_count += 1
            node_attrib = node.attrib
            node_id = node_attrib['id']
            node_lon = node_attrib['lon']
            node_lat = node_attrib['lat']
            print(f'[node]id:{node_id}, lon:{node_lon}, lat:{node_lat}')
            tags = node.findall('tag')
            for tag in tags:
                tag_attrib = tag.attrib
                tag_k = tag_attrib['k']
                tag_v = tag_attrib['v']
                print(f'tag k:{tag_k}, tag_v:{tag_v}')
                if tag_k == 'highway' and tag_v == 'crossing':
                    self.highway_cross_df = self.highway_cross_df.append({'id': node_id, 'lon': node_lon,
                                                                          'lat': node_lat}, ignore_index=True)
                    break
        self.nodes_count = temp_count

    def getHighwayCrossDf(self, boolWriteCSV=False):
        if boolWriteCSV:
            self.highway_cross_df.to_csv(self.interpreter_filename + '_highway_cross_wgs84.csv')
        return self.highway_cross_df


if __name__ == '__main__':
    ia = InterpreterAnalyse('shanghai_interpreter')
    ia.iterAllNodes()
    ia.getHighwayCrossDf(True)
