# Author: michael-gh1

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator


DIFFUSE_TEXTURE_KEY = 'Diffuse'
SMBE_TEXTURE_KEY = 'SMBE'
NORMAL_MAP_TEXTURE_KEY = 'Normal'


class B_OT_GenshinEnvironmentImportTextures(Operator, ImportHelper):
    """Import Environment Textures"""
    bl_idname = "genshin_environment.import_textures"
    bl_label = "Import Environ. Textures"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"
    
    import_path: StringProperty(
        name = "Path",
        description = "Path to the folder containing the files to import",
        default = "",
        subtype = 'DIR_PATH'
        )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def exec(self, context):
        directory = self.file_directory
        
        selected_mesh = bpy.context.active_object

        for name, folder, files in os.walk(directory):
            for file in files :
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                texture_image = bpy.data.images.load(filepath = img_path, check_existing=True)
                texture_image.alpha_mode = 'CHANNEL_PACKED'

                environment_shader_material = 'MATERIAL_GOES_HERE'  # TODO: make actual material, not string
                selected_mesh.material_slots[0] = environment_shader_material

                # Implement the texture in the correct node
                self.report({'INFO'}, f'Importing texture {file}')
                if DIFFUSE_TEXTURE_KEY in file:
                    self.import_diffuse_texture(environment_shader_material, texture_image)
                elif SMBE_TEXTURE_KEY in file:
                    self.import_smbe_texture(environment_shader_material, texture_image)
                elif NORMAL_MAP_TEXTURE_KEY in file:
                    self.import_normal_map_texture(environment_shader_material, texture_image)
                else :
                    pass
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

        self.report({'INFO'}, 'Imported textures')
        return {'FINISHED'}

    def import_diffuse_texture(self, material, diffuse_texture):
        self.import_texture(material, '', diffuse_texture)

    def import_smbe_texture(self, material, smbe_texture):
        self.import_texture(material, '', smbe_texture)

    def import_normal_map_texture(self, material, normal_map_texture):
        self.import_texture(material, '', normal_map_texture)

    def import_texture(self, material, node_name, texture):
        material.node_tree.nodes[node_name].image = texture
