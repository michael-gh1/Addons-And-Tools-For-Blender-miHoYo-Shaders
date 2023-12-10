# Author: michael-gh1

import bpy
import os

from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_material_names import JaredNytsPunishingGrayRavenShaderMaterialNames
from setup_wizard.geometry_nodes_setup.geometry_nodes_setups import PunishingGrayRavenGeometryNodesSetup

from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, JAREDNYTS_PGR_CHIBI_MESH_FILE_PATH, NextStepInvoker
from setup_wizard.import_order import NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.texture_import_setup.texture_node_names import JaredNytsPunishingGrayRavenTextureNodeNames


class PGR_OT_SetUpChibiFace(Operator, ImportHelper, CustomOperatorProperties):
    '''Set up ChibiFace mesh on armature'''
    bl_idname = 'punishing_gray_raven.set_up_chibi_face_mesh'
    bl_label = 'Select Emotes blend file'

    MESH_PATH_INSIDE_BLEND_FILE = 'Mesh'
    names_of_meshes = [
        {'name': 'ChibiFace'},
    ]
    material_names = JaredNytsPunishingGrayRavenShaderMaterialNames

    def execute(self, context):
        try:
            if not [material for material in bpy.data.materials if self.material_names.CHIBIFACE in material.name]:
                cache_enabled = context.window_manager.cache_enabled
                status = self.__import_chibi_face_mesh(cache_enabled)
                if status == {'FINISHED'}:
                    return status

                chibi_face_mesh = [obj for obj in bpy.data.objects if obj.name == self.material_names.CHIBIFACE][0]
                character_armature = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE'][0]

                self.__parent_mesh_to_armature(chibi_face_mesh, character_armature)
                self.__set_up_armature_modifier(chibi_face_mesh, character_armature)
                PunishingGrayRavenGeometryNodesSetup(self, context).create_light_vectors_modifier(chibi_face_mesh.name)

            self.report({'INFO'}, 'Finished setting up Chibi Face mesh')
            if self.next_step_idx:
                NextStepInvoker().invoke(
                    self.next_step_idx, 
                    self.invoker_type, 
                    high_level_step_name=self.high_level_step_name,
                    game_type=self.game_type,
                )
        except Exception as ex:
            raise ex
        finally:
            super().clear_custom_properties()
        return {'FINISHED'}

    def __import_chibi_face_mesh(self, cache_enabled):
        user_selected_shader_blend_file_path = self.filepath if \
            self.filepath and not os.path.isdir(self.filepath) else \
            get_cache(cache_enabled).get(JAREDNYTS_PGR_CHIBI_MESH_FILE_PATH)

        if not [material for material in bpy.data.materials if self.material_names.CHIBIFACE in material.name]:
            if not user_selected_shader_blend_file_path:
                # Use Case: Advanced Setup
                # The Operator is Executed directly with no cached files and so we need to Invoke to prompt the user
                bpy.ops.punishing_gray_raven.set_up_chibi_face_mesh(
                    'INVOKE_DEFAULT',
                    next_step_idx=self.next_step_idx, 
                    file_directory=self.file_directory,
                    invoker_type=self.invoker_type,
                    high_level_step_name=self.high_level_step_name,
                    game_type=self.game_type,
                )
                return {'FINISHED'}

            blend_file_with_meshes_filepath = os.path.join(
                user_selected_shader_blend_file_path,
                self.MESH_PATH_INSIDE_BLEND_FILE
            ) if user_selected_shader_blend_file_path else None

            try:
                bpy.ops.wm.append(
                    directory=blend_file_with_meshes_filepath,
                    files=self.names_of_meshes,
                    set_fake=True
                )
            except RuntimeError as ex:
                self.report({'ERROR'}, \
                    f"ERROR: Error when trying to append materials and Light Vector geometry node. \n\
                    Did not find `{blend_file_with_meshes_filepath}` in the directory you selected. \n\
                    Try selecting the exact blend file you want to use.")
                raise ex

            if cache_enabled and (user_selected_shader_blend_file_path):
                if user_selected_shader_blend_file_path:
                    cache_using_cache_key(get_cache(cache_enabled), JAREDNYTS_PGR_CHIBI_MESH_FILE_PATH, user_selected_shader_blend_file_path)

    def __parent_mesh_to_armature(self, chibi_face_mesh, character_armature):
        bpy.context.view_layer.objects.active = character_armature
        chibi_face_mesh.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    def __set_up_armature_modifier(self, chibi_face_mesh, character_armature):
            armature_modifier = chibi_face_mesh.modifiers.new(f'{character_armature.name}', 'ARMATURE')
            armature_modifier.object = character_armature


class PGR_OT_ImportChibiFaceTexture(Operator, ImportHelper, CustomOperatorProperties):
    '''Import Chibi Face Texture'''
    bl_idname = 'punishing_gray_raven.import_chibi_face_texture'
    bl_label = 'Select Character Folder'

    material_names = JaredNytsPunishingGrayRavenShaderMaterialNames
    texture_node_names = JaredNytsPunishingGrayRavenTextureNodeNames

    def execute(self, context):
        try:
            cache_enabled = context.window_manager.cache_enabled
            texture_directory = self.file_directory \
                or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
                or os.path.dirname(self.filepath)

            if not texture_directory:
                bpy.ops.punishing_gray_raven.import_chibi_face_texture(
                    'INVOKE_DEFAULT',
                    next_step_idx=self.next_step_idx, 
                    file_directory=self.file_directory,
                    invoker_type=self.invoker_type,
                    high_level_step_name=self.high_level_step_name,
                    game_type=GameType.PUNISHING_GRAY_RAVEN.name,
                )
                return {'FINISHED'}
            for name, folder, files in os.walk(texture_directory):
                for file in files:
                    # load the file with the correct alpha mode
                    img_path = texture_directory + "/" + file
                    img = bpy.data.images.load(filepath = img_path, check_existing=True)
                    img.alpha_mode = 'CHANNEL_PACKED'

                    print(f'Importing texture {file} using {self.__class__.__name__}')
                    if 'Base' in file:
                        chibi_face_material = bpy.data.materials.get(self.material_names.CHIBIFACE)
                        if chibi_face_material:
                            chibi_face_material.node_tree.nodes.get(self.texture_node_names.CHIBI_FACE).image = img
                break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

            if self.next_step_idx:
                NextStepInvoker().invoke(
                    self.next_step_idx, 
                    self.invoker_type, 
                    high_level_step_name=self.high_level_step_name,
                    game_type=self.game_type,
                )
        except Exception as ex:
            raise ex
        finally:
            super().clear_custom_properties()
        return {'FINISHED'}
