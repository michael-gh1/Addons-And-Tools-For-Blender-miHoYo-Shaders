import bpy
from bpy.props import EnumProperty
from bpy.types import Panel

from setup_wizard import bl_info
from setup_wizard.domain.game_types import GameType


class CSW_PT_Unified_Character_Setup_Wizard_UI_Layout(Panel):
    bl_label = "Character Setup Wizard"
    bl_idname = 'CSW_PT_Unified_Character_Setup_Wizard_UI_Layout'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Character Setup Wizard"

    bpy.types.Scene.game_type_dropdown = EnumProperty(
        items=[
            (GameType.GENSHIN_IMPACT.name, 'Genshin Impact', 'Genshin Impact Setup'),
            (GameType.HONKAI_STAR_RAIL.name, 'Honkai Star Rail', 'Honkai Star Rail Setup'),
            (GameType.PUNISHING_GRAY_RAVEN.name, 'Punishing Gray Raven', 'Punishing Gray Raven Setup'),
        ],
        name='Game',
        description='Setup for the selected game',
        default=GameType.GENSHIN_IMPACT.name,
    )

    def draw(self, context):
        layout = self.layout

        version_text = layout.row()
        version_text.label(text='v' + '.'.join([str(version_num) for version_num in bl_info.get('version')]))

        sub_layout = layout.box()
        sub_layout.prop(context.scene, 'game_type_dropdown')
