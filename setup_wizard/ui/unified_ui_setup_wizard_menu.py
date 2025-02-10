import bpy

from bpy.props import EnumProperty
from bpy.types import Panel

from setup_wizard.addon_updater import addon_updater_ops
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

    # Addon updater preferences.
    auto_check_update: bpy.props.BoolProperty(
        name='Auto-check for Update',
        description='If enabled, auto-check for updates using an interval',
        default=False
    )

    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)


    updater_interval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout

        version_text = layout.row()
        version_text.label(text='v' + '.'.join([str(version_num) for version_num in bl_info.get('version')]))

        col = layout.box().column()
        col.label(text=('(Experimental) Add-on Update'), icon='ERROR')
        addon_updater_ops.update_settings_ui_condensed(self, context, col)

        sub_layout = layout.box()
        sub_layout.prop(context.scene, 'game_type_dropdown')
