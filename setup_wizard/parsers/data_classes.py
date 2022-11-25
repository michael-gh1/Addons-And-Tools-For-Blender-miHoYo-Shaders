# Author: michael-gh1

'''
    Data class that is used to store values from m_Floats and m_Colors from Material Data Jsons
'''
class MaterialData:
    default_values = {
        '_MTSharpLayerOffset': 1.0
    }

    def __init__(self, json_m_data):
        for default_key, default_value in self.default_values.items():
            setattr(self, default_key, default_value)

        for key, value in json_m_data.items():
            setattr(self, key, value)
