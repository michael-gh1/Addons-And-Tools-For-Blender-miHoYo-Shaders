# Author: michael-gh1

from abc import ABC, abstractmethod

from setup_wizard.parsers.data_classes import MaterialData


class MaterialDataJsonParser(ABC):
    def __init__(self, json_material_data):
        self.json_material_data = json_material_data

    @abstractmethod
    def parse(self, json_material_data):
        raise NotImplementedError()


class HoyoStudioMaterialDataJsonParser(MaterialDataJsonParser):
    def __init__(self, json_material_data):
        super().__init__(json_material_data)

    def parse(self):
        m_colors = self.json_material_data.get('m_SavedProperties').get('m_Colors')
        m_colors_dict = {}
        for key, value in m_colors.items():
            m_colors_dict[key] = self.__get_rgba_colors(value)

        self.m_floats = MaterialData(self.json_material_data.get('m_SavedProperties').get('m_Floats'))
        self.m_colors = MaterialData(m_colors_dict)

    def get_rgba_colors(self, material_json_value):
        # check lowercase for backwards compatibility
        # explicitly check 'is not None' because rgba values could be Falsy
        r = material_json_value.get('R') if material_json_value.get('R') is not None else material_json_value.get('r')
        g = material_json_value.get('G') if material_json_value.get('G') is not None else material_json_value.get('g')
        b = material_json_value.get('B') if material_json_value.get('B') is not None else material_json_value.get('b')
        a = material_json_value.get('A') if material_json_value.get('A') is not None else material_json_value.get('a')
        return (r, g, b, a)


class UnknownHoyoStudioMaterialDataJsonParser(HoyoStudioMaterialDataJsonParser):
    def __init__(self, json_material_data):
        super().__init__(json_material_data)

    def parse(self):
        m_colors = self.json_material_data.get('m_SavedProperties').get('m_Colors')
        m_colors_dict = {}
        for m_colors_value_dict in m_colors:
            key = m_colors_value_dict['Key']
            value = m_colors_value_dict['Value']
            m_colors_dict[key] = self.get_rgba_colors(value)

        m_floats = self.json_material_data.get('m_SavedProperties').get('m_Floats')
        m_floats_dict = {}
        for m_floats_value_dict in m_floats:
            key = m_floats_value_dict['Key']
            value = m_floats_value_dict['Value']
            m_floats_dict[key] = value

        self.m_floats = MaterialData(m_floats_dict)
        self.m_colors = MaterialData(m_colors_dict)


class UABEMaterialDataJsonParser(MaterialDataJsonParser):
    def __init__(self, json_material_data):
        super().__init__(json_material_data)

    def parse(self):
        material_base = self.json_material_data.get('0 Material Base')
        m_saved_properties = material_base.get('0 UnityPropertySheet m_SavedProperties')

        json_m_floats = self.__get_json_m_floats(m_saved_properties)
        json_m_colors = self.__get_json_m_colors(m_saved_properties)
        
        self.m_floats = MaterialData(json_m_floats)
        self.m_colors = MaterialData(json_m_colors)

    def __get_json_m_floats(self, m_saved_properties):
        raw_m_floats = m_saved_properties.get('0 map m_Floats').get('0 Array Array')
        list_of_dict_m_floats = [
            {raw_m_float_json['0 pair data']['1 string first']: raw_m_float_json['0 pair data']['0 float second']}
            for raw_m_float_json in raw_m_floats
        ]  # a list of dictionaries

        json_m_floats = {}
        for dict_m_float in list_of_dict_m_floats:
            dict_m_float_key = list(dict_m_float.keys())[0]
            dict_m_float_value = list(dict_m_float.values())[0]

            json_m_floats[dict_m_float_key] = dict_m_float_value
        return json_m_floats

    def __get_json_m_colors(self, m_saved_properties):
        raw_m_colors = m_saved_properties.get('0 map m_Colors').get('0 Array Array')
        list_of_dict_m_colors = [
            {raw_m_float_json['0 pair data']['1 string first']: raw_m_float_json['0 pair data']['0 ColorRGBA second']}
            for raw_m_float_json in raw_m_colors
        ]  # a list of dictionaries

        json_m_colors = {}
        for dict_m_color in list_of_dict_m_colors:
            dict_m_color_key = list(dict_m_color.keys())[0]
            dict_m_color_value = list(dict_m_color.values())[0]

            json_m_colors[dict_m_color_key] = self.__get_rgba_colors(dict_m_color_value)
        return json_m_colors

    def __get_rgba_colors(self, material_json_value):
        prefix = '0 float'
        r = material_json_value.get(f'{prefix} r')
        g = material_json_value.get(f'{prefix} g')
        b = material_json_value.get(f'{prefix} b')
        a = material_json_value.get(f'{prefix} a')
        return (r, g, b, a)
