import bpy
from bpy.types import Panel, UILayout


class GI_PT_Setup_Wizard_UI_Layout(Panel):
    bl_label = "Genshin Impact Setup Wizard"
    bl_idname = "GI_PT_Setup_Wizard_UI_Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Genshin"

    def draw(self, context):
        layout = self.layout


class GI_PT_UI_Character_Model_Menu(Panel):
    bl_label = 'Character Model Menu'
    bl_idname = 'GI_PT_UI_Character_Model_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        # layout.operator(
        #     operator='', 
        #     text='Setup Character Model',
        #     icon='OUTLINER_OB_ARMATURE'
        # )
        
        box = layout.box()
        OperatorFactory.create(
            box,
            'genshin.import_model',
            'Import Character Model',
            'OUTLINER_OB_ARMATURE'
        )
        OperatorFactory.create(
            box,
            'genshin.delete_empties',
            'Delete Empties',
            'TRASH'
        )


class GI_PT_UI_Materials_Menu(Panel):
    bl_label = 'Materials Menu'
    bl_idname = 'GI_PT_UI_Materials_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        OperatorFactory.create(
            box,
            'genshin.import_materials',
            'Import Genshin Materials',
            'MATERIAL'
        )
        OperatorFactory.create(
            box,
            'genshin.replace_default_materials',
            'Replace Default Materials',
            'ARROW_LEFTRIGHT'
        )
        OperatorFactory.create(
            box,
            'genshin.import_textures',
            'Import Character Textures',
            'TEXTURE'
        )


class GI_PT_UI_Outlines_Menu(Panel):
    bl_label = 'Outlines Menu'
    bl_idname = 'GI_PT_UI_Outlines_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        OperatorFactory.create(
            box,
            'genshin.import_outlines',
            'Import Outlines',
            'FILE_FOLDER'
        )
        OperatorFactory.create(
            box,
            'genshin.setup_geometry_nodes',
            'Set Up Geometry Nodes',
            'GEOMETRY_NODES'
        )
        OperatorFactory.create(
            box,
            'genshin.import_outline_lightmaps',
            'Import Outline Lightmaps',
            'FILE_FOLDER'
        )
        OperatorFactory.create(
            box,
            'genshin.import_material_data',
            'Import Material Data',
            'FILE'
        )


class GI_PT_UI_Misc_Setup_Menu(Panel):
    bl_label = 'Misc Setup Menu'
    bl_idname = 'GI_PT_UI_Misc_Setup_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        OperatorFactory.create(
            box,
            'genshin.make_character_upright',
            'Make Character Upright',
            'OBJECT_DATA'
        )
        OperatorFactory.create(
            box,
            'genshin.setup_head_driver',
            'Set Up Head Driver',
            'CONSTRAINT'
        )


class GI_PT_UI_Misc_Menu(Panel):
    bl_label = 'Misc Menu'
    bl_idname = 'GI_PT_UI_Misc_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_Setup_Wizard_UI_Layout'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        OperatorFactory.create(
            box,
            'genshin.set_color_management_to_standard',
            'Set Color Mgmt to Standard',
            'SCENE'
        )
        OperatorFactory.create(
            box,
            'genshin.delete_specific_objects',
            'Delete EffectMesh',
            'TRASH'
        )


'''
    This factory is intended to help create a UI element's operator (or the action it takes) when pressed.
    While it currently doesn't do anything too grand, it may provide future flexibility.
'''
class OperatorFactory:
    @staticmethod
    def create(ui_object: UILayout, operator: str, text: str, icon: str):
        ui_object.operator(
            operator=operator,
            text=text,
            icon=icon,
        )
