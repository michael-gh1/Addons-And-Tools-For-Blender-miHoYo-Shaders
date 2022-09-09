# Author: michael-gh1

class UnsupportedMaterialDataJsonFormatException(Exception):
    def __init__(self, parsers):
        message = 'Unable to determine Material Data Json Parser to use. ' \
            'Unsupported Material Data Json format detected. ' \
                f'Supported Material Data Json Formats: {parsers}'
        super().__init__(message)

class MaterialDataValueNotFoundException(Exception):
    def __init__(self, body_part, material_json_name):
        message = f'Error! Could not find {material_json_name} in {body_part} JSON file'
        super().__init__(message)
