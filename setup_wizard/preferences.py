import bpy

from setup_wizard.addon_updater import addon_updater_ops


@addon_updater_ops.make_annotations
class CharacterSetupWizardAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # Addon updater preferences
    auto_check_update: bpy.props.BoolProperty(
        name='Auto-check for Update',
        description='If enabled, auto-check for updates using an interval',
        default=False
    )

    updater_interval_months: bpy.props.IntProperty(
        name='Months',
        description='Number of months between checking for updates',
        default=0,
        min=0
    )

    updater_interval_days: bpy.props.IntProperty(
        name='Days',
        description='Number of days between checking for updates',
        default=7,
        min=0,
        max=31
    )

    updater_interval_hours: bpy.props.IntProperty(
        name='Hours',
        description='Number of hours between checking for updates',
        default=0,
        min=0,
        max=23
    )

    updater_interval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description='Number of minutes between checking for updates',
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout

        col = layout.box().column()
        col.label(text=('(Experimental) Add-on Update'), icon='ERROR')
        addon_updater_ops.update_settings_ui(self, context, col)
