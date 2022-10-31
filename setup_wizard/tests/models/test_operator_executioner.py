from setup_wizard.import_order import ComponentFunctionFactory
from setup_wizard.tests.constants import MATERIAL_JSON_FOLDER_FILE_PATH


class TestOperatorExecutioner:
    def __init__(self, operator_name, file_directory='', filepath='', files=[], config={}):
        self.operator_name = operator_name
        self.file_directory = file_directory
        self.filepath = filepath
        self.files = files
        self.config = config

    def execute(self):
        operator_to_execute = ComponentFunctionFactory.create_component_function(self.operator_name)

        if self.files:
            operator_to_execute(
                'EXEC_DEFAULT',
                files=self.files,
                filepath=self.config.get(MATERIAL_JSON_FOLDER_FILE_PATH),
            )
        elif self.file_directory or self.filepath:
            operator_to_execute(
                'EXEC_DEFAULT',
                file_directory=self.file_directory,
                filepath=self.filepath
            )
        else:
            operator_to_execute(
                'EXEC_DEFAULT'
            )
