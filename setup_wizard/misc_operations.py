# Author: michael-gh1

import bpy
from bpy.types import Material, Operator

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_identifier_service import ShaderIdentifierService, ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import ShaderMaterialNames
from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.texture_import_setup.texture_node_names import TextureNodeNames


class GI_OT_SetColorManagementToStandard(Operator, CustomOperatorProperties):
    '''Sets Color Management to Standard'''
    bl_idname = 'genshin.set_color_management_to_standard'
    bl_label = 'Genshin: Set Color Management to Standard'

    def execute(self, context):
        bpy.context.scene.view_settings.view_transform = 'Standard'

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}


class GI_OT_DeleteSpecificObjects(Operator, CustomOperatorProperties):
    '''Deletes EffectMesh'''
    bl_idname = 'genshin.delete_specific_objects'
    bl_label = 'Genshin: Delete EffectMesh'

    def execute(self, context):
        scene = bpy.context.scene
        objects_to_delete = [
            'EffectMesh'
        ]  # be extremely careful, we will be deleting anything that contains these object names

        for object in scene.objects:
            for object_to_delete in objects_to_delete:
                if object_to_delete in object.name and object.type == 'MESH':
                    bpy.data.objects.remove(object)

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}


class GI_OT_RenameShaderMaterials(Operator, CustomOperatorProperties):
    '''Renames Shader Materials with Character Names'''
    bl_idname = 'hoyoverse.rename_shader_materials'
    bl_label = 'HoYoverse: Rename Shader Materials'

    def execute(self, context):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(self.game_type)
        shader_material_names = shader_identifier_service.get_shader_material_names(
            self.game_type, bpy.data.materials, bpy.data.node_groups
        )
        body_material: Material = bpy.data.materials.get(shader_material_names.BODY) or \
            bpy.data.materials.get(shader_material_names.BODY1)

        texture_node_names: TextureNodeNames = shader_identifier_service.get_shader_texture_node_names(
            self.game_type, bpy.data.materials, bpy.data.node_groups
        )
        body_diffuse_uv0_node_name = texture_node_names.BODY_DIFFUSE_UV0 or texture_node_names.DIFFUSE

        if body_material:
            body_diffuse_texture = body_material.node_tree.nodes.get(body_diffuse_uv0_node_name).image
            if body_diffuse_texture:
                materials_to_check = [material for material in bpy.data.materials if \
                                    material.name.startswith(shader_material_names.MATERIAL_PREFIX)]
                for material in materials_to_check:
                    self.__set_material_names(self.game_type, material, shader_material_names, body_diffuse_texture.name)

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}

    def __set_material_names(self, game_type: GameType, material: Material, shader_material_names: ShaderMaterialNames, body_diffuse_filename):
        if game_type == GameType.HONKAI_STAR_RAIL.name:
            character_name = body_diffuse_filename.split('_')[1]
        elif game_type == GameType.GENSHIN_IMPACT.name:
            character_name = body_diffuse_filename.split('_')[3]
        else:
            return
        second_half_of_material_prefix = shader_material_names.MATERIAL_PREFIX.split('-')[1]
        material.name = material.name.replace(f'-{second_half_of_material_prefix}', f'- {character_name} ')


class GI_OT_SetUpArmTwistBoneConstraints(Operator, CustomOperatorProperties):
    '''Sets Up ArmTwist Bone Constraints'''
    bl_idname = 'genshin.set_up_armtwist_bone_constraints'
    bl_label = 'Genshin: Set Up ArmTwist Bone Constraints'

    LEFT_ARMTWIST_A01 = '+UpperArmTwist L A01'
    LEFT_ARMTWIST_A02 = '+UpperArmTwist L A02'
    RIGHT_ARMTWIST_A01 = '+UpperArmTwist R A01'
    RIGHT_ARMTWIST_A02 = '+UpperArmTwist R A02'

    ARMTWIST_A01_INFLUENCE = 0.35
    ARMTWIST_A02_INFLUENCE = 0.65

    LEFT_FOREARM = 'Bip001 L Forearm'
    RIGHT_FOREARM = 'Bip001 R Forearm'

    def execute(self, context):
        armature =  [object for object in bpy.data.objects if object.type == 'ARMATURE'][0]
        left_armtwist_bone_names = [
            self.LEFT_ARMTWIST_A01,
            self.LEFT_ARMTWIST_A02,
        ]
        right_armtwist_bone_names = [
            self.RIGHT_ARMTWIST_A01,
            self.RIGHT_ARMTWIST_A02,
        ]

        self.reorient_armtwist_bones(armature, left_armtwist_bone_names, self.LEFT_FOREARM)
        self.reorient_armtwist_bones(armature, right_armtwist_bone_names, self.RIGHT_FOREARM)

        self.set_up_armtwist_bone_constraint(armature, self.LEFT_ARMTWIST_A01, self.LEFT_FOREARM, self.ARMTWIST_A01_INFLUENCE)
        self.set_up_armtwist_bone_constraint(armature, self.LEFT_ARMTWIST_A02, self.LEFT_FOREARM, self.ARMTWIST_A02_INFLUENCE)
        self.set_up_armtwist_bone_constraint(armature, self.RIGHT_ARMTWIST_A01, self.RIGHT_FOREARM, self.ARMTWIST_A01_INFLUENCE)
        self.set_up_armtwist_bone_constraint(armature, self.RIGHT_ARMTWIST_A02, self.RIGHT_FOREARM, self.ARMTWIST_A02_INFLUENCE)

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}

    def reorient_armtwist_bones(self, armature, bone_names, target_bone_name):
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        for bone_name in bone_names:
            bone = armature.data.edit_bones.get(bone_name)
            target_bone = armature.data.edit_bones.get(target_bone_name)

            if bone and target_bone:
                original_bone_length = bone.length
                bone.tail = target_bone.head
                bone.length = original_bone_length

        bpy.ops.object.mode_set(mode='OBJECT')

    def set_up_armtwist_bone_constraint(self, armature, bone_name, subtarget_bone_name, influence):
        armature_bones = armature.pose.bones
        twist_bone = armature_bones.get(bone_name)

        if twist_bone and subtarget_bone_name:
            copy_rotation_constraint = twist_bone.constraints.new('COPY_ROTATION')
            copy_rotation_constraint.target = armature
            copy_rotation_constraint.subtarget = subtarget_bone_name
            copy_rotation_constraint.use_x = False
            copy_rotation_constraint.use_z = False
            copy_rotation_constraint.target_space = 'LOCAL'
            copy_rotation_constraint.owner_space = 'LOCAL'
            copy_rotation_constraint.influence = influence
            return copy_rotation_constraint


register, unregister = bpy.utils.register_classes_factory([
    GI_OT_SetColorManagementToStandard,
    GI_OT_DeleteSpecificObjects,
    GI_OT_SetUpArmTwistBoneConstraints,
])
