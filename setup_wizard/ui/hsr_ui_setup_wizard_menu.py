# Author: michael-gh1

import bpy
from bpy.types import Panel, UILayout

from setup_wizard.domain.game_types import GameType
from setup_wizard.ui.ui_render_checker import HonkaiStarRailUIRenderChecker


class HSR_PT_Setup_Wizard_UI_Layout(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = "Honkai Star Rail Setup Wizard"
    bl_idname = "HSR_PT_Setup_Wizard_UI_Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Character Setup Wizard"

    def draw(self, context):
        layout = self.layout
        window_manager = context.window_manager

        sub_layout = layout.box()
        run_entire_setup_column = sub_layout.column()
        OperatorFactory.create(
            run_entire_setup_column,
            'honkai_star_rail.setup_wizard_ui',
            'Run Entire Setup',
            'PLAY',
            game_type=GameType.HONKAI_STAR_RAIL.name
        )
        OperatorFactory.create_betterfbx_required_ui(run_entire_setup_column)

        expy_kit_installed = bpy.context.preferences.addons.get('Expy-Kit-main')
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        rigify_installed = bpy.context.preferences.addons.get('rigify')

        if not expy_kit_installed or not betterfbx_installed or not rigify_installed:
            sub_layout.label(text='Rigging Disabled', icon='ERROR')

        settings_box = layout.box()
        settings_box.label(text='Global Settings', icon='WORLD')

        row = settings_box.row()
        row.prop(window_manager, 'cache_enabled')
        OperatorFactory.create(
            row,
            'genshin.clear_cache_operator',
            'Clear Cache',
            'TRASH',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )

        # settings_box.prop(window_manager, 'setup_wizard_full_run_rigging_enabled')  # temp disabled, feature preview only

class HSR_PT_Basic_Setup_Wizard_UI_Layout(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = 'Basic Setup'
    bl_idname = 'HSR_PT_UI_Basic_Setup_Layout'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character Setup Wizard"

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.box()

        set_up_character_column = sub_layout.column()
        OperatorFactory.create(
            set_up_character_column,
            'honkai_star_rail.set_up_character',
            'Set Up Character',
            icon='OUTLINER_OB_ARMATURE',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        OperatorFactory.create_betterfbx_required_ui(set_up_character_column)

        OperatorFactory.create(
            sub_layout,
            'honkai_star_rail.set_up_materials',
            'Set Up Materials',
            icon='MATERIAL',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        if bpy.app.version >= (3,3,0):
            OperatorFactory.create(
                sub_layout,
                'honkai_star_rail.set_up_outlines',
                'Set Up Outlines',
                icon='GEOMETRY_NODES',
                game_type=GameType.HONKAI_STAR_RAIL.name,
            )
        else:
            layout.label(text='(Outlines Disabled < v3.3.0)')
        OperatorFactory.create(
            sub_layout,
            'honkai_star_rail.finish_setup',
            'Finish Setup',
            icon='CHECKMARK',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )

        OperatorFactory.create_rig_character_ui(sub_layout)


class HSR_PT_Advanced_Setup_Wizard_UI_Layout(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = 'Advanced Setup'
    bl_idname = 'HSR_PT_UI_Advanced_Setup_Layout'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character Setup Wizard"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


class HSR_PT_UI_Character_Model_Menu(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = 'Set Up Character Menu'
    bl_idname = 'HSR_PT_UI_Character_Model_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'HSR_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.box()

        import_character_model_column = sub_layout.column()
        OperatorFactory.create(
            import_character_model_column,
            'genshin.import_model',
            'Import Character Model',
            'OUTLINER_OB_ARMATURE',
        )
        OperatorFactory.create_betterfbx_required_ui(import_character_model_column)

        OperatorFactory.create(
            sub_layout,
            'genshin.delete_empties',
            'Delete Empties',
            'TRASH'
        )


class HSR_PT_UI_Materials_Menu(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = 'Set Up Materials Menu'
    bl_idname = 'HSR_PT_UI_Materials_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'HSR_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()

        OperatorFactory.create(
            sub_layout,
            'genshin.import_materials',
            'Import HSR Materials',
            'MATERIAL',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.replace_default_materials',
            'Replace Default Materials',
            'ARROW_LEFTRIGHT',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.import_textures',
            'Import Character Textures',
            'TEXTURE',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )


class HSR_PT_UI_Outlines_Menu(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = 'Set Up Outlines Menu'
    bl_idname = 'HSR_PT_UI_Outlines_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'HSR_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()
        scene = context.scene

        if bpy.app.version >= (3,3,0):
            OperatorFactory.create(
                sub_layout,
                'genshin.import_outlines',
                'Import Outlines',
                'FILE_FOLDER',
                game_type=GameType.HONKAI_STAR_RAIL.name,
            )
            OperatorFactory.create(
                sub_layout,
                'genshin.setup_geometry_nodes',
                'Set Up Geometry Nodes',
                'GEOMETRY_NODES',
                game_type=GameType.HONKAI_STAR_RAIL.name,
            )
            OperatorFactory.create(
                sub_layout,
                'genshin.import_outline_lightmaps',
                'Import Outline Lightmaps',
                'FILE_FOLDER',
                game_type=GameType.HONKAI_STAR_RAIL.name,
            )

            sub_layout = layout.box()
            sub_layout.prop_search(scene, 'setup_wizard_material_for_material_data_import', bpy.data, 'materials')
            sub_layout.prop_search(scene, 'setup_wizard_outlines_material_for_material_data_import', bpy.data, 'materials')
            OperatorFactory.create(
                sub_layout,
                'genshin.import_material_data',
                'Import Material Data',
                'FILE',
                game_type=GameType.HONKAI_STAR_RAIL.name,
                setup_mode='ADVANCED'
            )
        else:
            layout.label(text='(Outlines Disabled < v3.3.0)')


class HSR_PT_UI_Finish_Setup_Menu(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = 'Finish Setup Menu'
    bl_idname = 'HSR_PT_UI_Misc_Setup_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'HSR_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()

        OperatorFactory.create(
            sub_layout,
            'genshin.fix_transformations',
            'Fix Transformations',
            'OBJECT_DATA'
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.setup_head_driver',
            'Set Up Head Driver',
            'CONSTRAINT'
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.set_color_management_to_standard',
            'Set Color Mgmt to Standard',
            'SCENE'
        )
        OperatorFactory.create(
            sub_layout,
            'hoyoverse.set_up_screen_space_reflections',
            'Enable SSR',
            'SCENE',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        OperatorFactory.create(
            sub_layout,
            'hoyoverse.vertex_paint_face_see_through_effect',
            'Vertex Paint Face',
            'VPAINT_HLT',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.delete_specific_objects',
            'Clean Up Extra Meshes',
            'TRASH'
        )
        OperatorFactory.create(
            sub_layout,
            'hoyoverse.rename_shader_materials',
            'Rename Shader Materials',
            'GREASEPENCIL',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.set_up_armtwist_bone_constraints',
            'Set Up ArmTwist Bone Constraints',
            'CONSTRAINT_BONE'
        )


class HSR_PT_UI_Character_Rig_Setup_Menu(Panel, HonkaiStarRailUIRenderChecker):
    bl_label = 'Character Rig Menu'
    bl_idname = 'HSR_PT_Rigify_Setup_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'HSR_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()
        box = sub_layout.box()

        character_rigger_props = context.scene.character_rigger_props

        OperatorFactory.create_rig_character_ui(box)

        box = sub_layout.box()        
        box.label(text='Settings')

        col = box.column()
        OperatorFactory.create(
            col,
            'hoyoverse.rootshape_filepath_setter',
            'Override RootShape Filepath',
            'FILE_FOLDER',
            game_type=GameType.HONKAI_STAR_RAIL.name,
            operator_context='INVOKE_DEFAULT'
        )
        col = box.column()
        col.prop(character_rigger_props, 'allow_arm_ik_stretch')
        col.prop(character_rigger_props, 'allow_leg_ik_stretch')
        col.prop(character_rigger_props, 'use_arm_ik_poles')
        col.prop(character_rigger_props, 'use_leg_ik_poles')
        col.prop(character_rigger_props, 'add_children_of_constraints')
        col.prop(character_rigger_props, 'use_head_tracker')


# class HSR_PT_UI_Compositing_Panel_Post_Processing_UI_Layout(Panel, HonkaiStarRailUIRenderChecker):
#     bl_label = "Compositing Setup Wizard"
#     bl_idname = "HSR_PT_Custom_Compositing_Node_UI_Layout"
#     bl_space_type = "NODE_EDITOR"
#     bl_region_type = "UI"
#     bl_category = "HSR - Setup Wizard"

#     def draw(self, context):
#         layout = self.layout
#         row = layout.row()
#         sub_layout = layout.box()
#         window_manager = context.window_manager

#         row.prop(window_manager, 'cache_enabled')
#         OperatorFactory.create(
#             row,
#             'genshin.clear_cache_operator',
#             'Clear Cache',
#             'TRASH',
#             game_type=GameType.HONKAI_STAR_RAIL.name,
#         )
#         OperatorFactory.create(
#             sub_layout,
#             'genshin.change_bpy_context',
#             'Enable Use Nodes',
#             'CHECKMARK',
#             bpy_context_attr='scene.use_nodes',
#             bpy_context_value_bool=True
#         )
#         OperatorFactory.create(
#             sub_layout,
#             'hoyoverse.custom_composite_node_setup',
#             'Set Up Compositing Node',
#             'PLAY'
#         )


'''
    This factory is intended to help create a UI element's operator (or the action it takes) when pressed.
    While it currently doesn't do anything too grand, it may provide future flexibility.
'''
class OperatorFactory:
    @staticmethod
    def create(
        ui_object: UILayout,
        operator: str,
        text: str,
        icon: str,
        operator_context='EXEC_DEFAULT',
        **kwargs
    ):
        ui_object.operator_context = operator_context
        ui_object = ui_object.operator(
            operator=operator,
            text=text,
            icon=icon,
        )

        for key, value in kwargs.items():
            setattr(ui_object, key, value)

    @staticmethod
    def create_betterfbx_required_ui(
        ui_object: UILayout,
    ):
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        if not betterfbx_installed:
            ui_object.column()
            ui_object.enabled = False
            ui_object.label(text='BetterFBX required', icon='ERROR')

    @staticmethod
    def create_rig_character_ui(
        ui_object: UILayout,
    ):
        expy_kit_installed = bpy.context.preferences.addons.get('Expy-Kit-main')
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        rigify_installed = bpy.context.preferences.addons.get('rigify')

        column = ui_object.column()
        column.enabled = True if expy_kit_installed and betterfbx_installed and rigify_installed else False
        OperatorFactory.create(
            column,
            'hoyoverse.set_up_character_rig',
            'Rig Character [Preview]',
            'OUTLINER_OB_ARMATURE',
            game_type=GameType.HONKAI_STAR_RAIL.name,
        )
        if not column.enabled:
            column = ui_object.column()
            if not betterfbx_installed:
                column.label(text='BetterFBX required', icon='ERROR')
            if not expy_kit_installed:
                column.label(text='ExpyKit required', icon='ERROR')
            if not rigify_installed:
                column.label(text='Rigify required', icon='ERROR')
