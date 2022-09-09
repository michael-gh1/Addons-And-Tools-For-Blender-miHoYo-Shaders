# Author: michael-gh1

class UnsupportedMaterialDataJsonFormatException(Exception):
    def __init__(self, parsers):
        message = 'Unable to determine Material Data Json Parser to use. ' \
            'Unsupported Material Data Json format detected. ' \
                f'Supported Material Data Json Formats: {parsers}'
        super().__init__(message)
