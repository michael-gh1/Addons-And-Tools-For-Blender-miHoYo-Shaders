# Author: michael-gh1

'''
    Data class that is used to store values from m_Floats and m_Colors from Material Data Jsons
'''
class MaterialData:
    def __init__(self, json_m_data):
        for key, value in json_m_data.items():
            setattr(self, key, value)
