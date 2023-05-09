from setup_wizard.domain.game_types import GameType
from setup_wizard.import_order import ComponentFunctionFactory
from setup_wizard.tests.constants import MATERIAL_JSON_FOLDER_FILE_PATH


class TestOperatorExecutioner:
    def __init__(self, operator_name, file_directory='', filepath='', files=[], config={}, game_type=''):
        self.operator_name = operator_name
        self.file_directory = file_directory
        self.filepath = filepath
        self.files = files
        self.config = config
        self.game_type = game_type

    def execute(self):
        operator_to_execute = ComponentFunctionFactory.create_component_function(self.operator_name)

        if self.files:
            operator_to_execute(
                'EXEC_DEFAULT',
                files=self.files,
                filepath=self.filepath or self.config.get(MATERIAL_JSON_FOLDER_FILE_PATH),
                game_type=self.game_type,
            )
        elif self.file_directory or self.filepath:
            operator_to_execute(
                'EXEC_DEFAULT',
                file_directory=self.file_directory,
                filepath=self.filepath,
                game_type=self.game_type,
            )
        else:
            if self.game_type:
                operator_to_execute(
                    'EXEC_DEFAULT',
                    game_type=self.game_type
                )
            else:
                operator_to_execute(
                    'EXEC_DEFAULT'
                )


class GenshinImpactTestOperatorExecutioner(TestOperatorExecutioner):
    def __init__(self, operator_name, file_directory='', filepath='', files=[], config={}):
        super().__init__(operator_name, file_directory, filepath, files, config, GameType.GENSHIN_IMPACT.name)


class HonkaiStarRailTestOperatorExecutioner(TestOperatorExecutioner):
    def __init__(self, operator_name, file_directory='', filepath='', files=[], config={}):
        super().__init__(operator_name, file_directory, filepath, files, config, GameType.HONKAI_STAR_RAIL.name)
