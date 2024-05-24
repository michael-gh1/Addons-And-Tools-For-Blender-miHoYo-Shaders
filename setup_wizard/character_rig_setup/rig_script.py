# Authors: enthralpy, Llama.jpg
# Setup Wizard Integration by michael-gh1

import bpy
import os
from mathutils import Color, Vector
from math import pi

from setup_wizard.geometry_nodes_setup.lighting_panel_names import LightingPanelNames

def rig_character(
        file_path, 
        disallow_arm_ik_stretch, 
        disallow_leg_ik_stretch,
        use_arm_ik_poles,
        use_leg_ik_poles,
        add_child_of_constraints,
        use_head_tracker,
        meshes_joined=False):
    
    # Firstly, let's make a flag to identify the blender version.
    is_version_4 = False
    version_string = bpy.app.version_string
    if version_string[0] == "4":
        is_version_4 = True
               
    head_bone_arm_target = bpy.context.active_object
    temp_armature = head_bone_arm_target.data

    bpy.ops.object.mode_set(mode='EDIT')

    # Check if toe bones exist
    toe_bones_exist = True
    if "Bip001 L Toe0" not in temp_armature.edit_bones:
        toe_bones_exist = False

    # Check if eyes exist:
    left_eye_exists = True
    if "+EyeBone L A02" not in temp_armature.edit_bones:
        left_eye_exists = False

    right_eye_exists = True
    if "+EyeBone R A02" not in temp_armature.edit_bones:
        right_eye_exists = False

    no_eyes = False    
    if not left_eye_exists and not right_eye_exists:
          no_eyes = True
        
    # Hoyo models have inconsistent head bone shapes. I'm correcting them to my standard. (This stabilizes the head track bone)
    # My logic: Line up the head bone's tail's X & Y to the head bone's head (so that it's straight up), and use the eye bone's head's Z as the height. - Llama    
    if not no_eyes:
        if left_eye_exists:
            eye_bone_head = temp_armature.edit_bones['+EyeBone L A02']
        elif right_eye_exists:
            eye_bone_head = temp_armature.edit_bones['+EyeBone R A02']
        eye_bone_head_z = eye_bone_head.head[2]

        head_bone_temp = temp_armature.edit_bones['Bip001 Head']
        head_bone_head_x = head_bone_temp.head[0]
        head_bone_head_y = head_bone_temp.head[1]

        head_bone_temp.tail[0] = head_bone_head_x
        head_bone_temp.tail[1] = head_bone_head_y
        head_bone_temp.tail[2] = eye_bone_head_z
        
    # If they dont have eye bones (Dottore), we can hardcode a reasonable value to use to repair the head.
    else:
        head_bone_temp = temp_armature.edit_bones['Bip001 Head']
        head_bone_head_x = head_bone_temp.head[0]
        head_bone_head_y = head_bone_temp.head[1]

        head_bone_temp.tail[0] = head_bone_head_x
        head_bone_temp.tail[1] = head_bone_head_y
        head_bone_temp.tail[2] = head_bone_temp.head[2] + 0.0538
        
    left_eye_2 = []
    left_eye_1 = []
    right_eye_2 = []
    right_eye_1 = []

    if left_eye_exists:
        left_eye_2.append(temp_armature.edit_bones['+EyeBone L A02'].head[0])       
        left_eye_2.append(temp_armature.edit_bones['+EyeBone L A02'].head[1])       
        left_eye_2.append(temp_armature.edit_bones['+EyeBone L A02'].head[2])
        
        left_eye_1.append(temp_armature.edit_bones['+EyeBone L A01'].head[0])       
        left_eye_1.append(temp_armature.edit_bones['+EyeBone L A01'].head[1])       
        left_eye_1.append(temp_armature.edit_bones['+EyeBone L A01'].head[2])       
    if right_eye_exists:
        right_eye_2.append(temp_armature.edit_bones['+EyeBone R A02'].head[0])       
        right_eye_2.append(temp_armature.edit_bones['+EyeBone R A02'].head[1])       
        right_eye_2.append(temp_armature.edit_bones['+EyeBone R A02'].head[2])
        
        right_eye_1.append(temp_armature.edit_bones['+EyeBone R A01'].head[0])       
        right_eye_1.append(temp_armature.edit_bones['+EyeBone R A01'].head[1])       
        right_eye_1.append(temp_armature.edit_bones['+EyeBone R A01'].head[2])  
            
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # THANK YOU: https://blenderartists.org/t/how-to-bpy-ops-transform-resize-in-edit-mode-using-pivot/560381/2
    def get_override(area_type, region_type):
        for area in bpy.context.screen.areas: 
            if area.type == area_type:             
                for region in area.regions:                 
                    if region.type == region_type:                    
                        override = {'area': area, 'region': region} 
                        return override
        #error message if the area or region wasn't found
        raise RuntimeError("Wasn't able to find", region_type," in area ", area_type, " Make sure it's open while executing script.")

    #we need to override the context of our operator    
    override = get_override( 'VIEW_3D', 'WINDOW' )

    # Function to create shape keys from given arguments: Works with only one element in vg to parse
    def create_shape_key(obj_get, is_basis, shape_name, transform_pivot, vertex_groups_to_parse, transform_type, transformation_1, transformation_2=0, use_eye_1=False):
        bpy.context.view_layer.objects.active = head_bone_arm_target
        bpy.ops.object.mode_set(mode='EDIT')
        for this_group in vertex_groups_to_parse:
            if use_eye_1:
                if " R " in this_group:
                    if right_eye_exists:
                        bpy.context.scene.cursor.location = (right_eye_1[0],right_eye_1[1],right_eye_1[2])
                elif " L " in this_group:
                    if left_eye_exists:
                        bpy.context.scene.cursor.location = (left_eye_1[0],left_eye_1[1],left_eye_1[2])
            else:
                if " R " in this_group:
                    if right_eye_exists:
                        bpy.context.scene.cursor.location = (right_eye_2[0],right_eye_2[1],right_eye_2[2])
                elif " L " in this_group:
                    if left_eye_exists:
                        bpy.context.scene.cursor.location = (left_eye_2[0],left_eye_2[1],left_eye_2[2])
                        
            # AFTER MOVING 3D CURSOR
            this_obj = bpy.data.objects.get(obj_get)
            bpy.context.view_layer.objects.active = this_obj
            
            if is_basis:
                this_obj.shape_key_add(name='Basis')
                
            this_obj.shape_key_add(from_mix=False)   
            sk = this_obj.data.shape_keys.key_blocks[-1]
            sk.name = shape_name
            sk.value = 1
            shape_index = this_obj.data.shape_keys.key_blocks.keys().index(shape_name)
            bpy.context.object.active_shape_key_index = shape_index
            
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.context.tool_settings.transform_pivot_point = "CURSOR"   
        
            try:
                bpy.ops.object.vertex_group_set_active(group=this_group)
                bpy.ops.object.vertex_group_select()
                
                if transform_type == "RESIZE":
                    # for documentation: v4 does not like the override argument lmao
                    if not is_version_4:
                        bpy.ops.transform.resize(override, value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    else:
                        bpy.ops.transform.resize(value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.object.vertex_group_deselect()
                elif transform_type == "TRANSLATE":
                    if not is_version_4:
                        bpy.ops.transform.translate(override, value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                        bpy.ops.transform.resize(override, value=transformation_2)
                        bpy.ops.object.vertex_group_deselect()
                    else:
                        bpy.ops.transform.translate(value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                        bpy.ops.transform.resize(override, value=transformation_2)
                        bpy.ops.object.vertex_group_deselect()                    
            except:
                pass
        
            bpy.ops.object.vertex_group_deselect()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            sk.value = 0.0
            bpy.context.scene.cursor.location = (0.0,0.0,0.0)
      
    # Function to create shape keys that works with 2 elementsa        
    def create_shape_key2(obj_get, is_basis, shape_name, transform_pivot, vertex_groups_to_parse, transform_type, transformation_1, transformation_2=0, use_eye_1=False):
        bpy.context.view_layer.objects.active = head_bone_arm_target
        bpy.ops.object.mode_set(mode='EDIT')
        if use_eye_1:
            if " R " in vertex_groups_to_parse[0]:
                if right_eye_exists:
                    bpy.context.scene.cursor.location = (right_eye_1[0],right_eye_1[1],right_eye_1[2])
            elif " L " in vertex_groups_to_parse[0]:
                if left_eye_exists:
                    bpy.context.scene.cursor.location = (left_eye_1[0],left_eye_1[1],left_eye_1[2])
        else:
            if " R " in vertex_groups_to_parse[0]:
                if right_eye_exists:
                    bpy.context.scene.cursor.location = (right_eye_2[0],right_eye_2[1],right_eye_2[2])
            elif " L " in vertex_groups_to_parse[0]:
                if left_eye_exists:
                    bpy.context.scene.cursor.location = (left_eye_2[0],left_eye_2[1],left_eye_2[2])
                        
        # AFTER MOVING 3D CURSOR
        this_obj = bpy.data.objects.get(obj_get)
        bpy.context.view_layer.objects.active = this_obj
        
        if is_basis:
            this_obj.shape_key_add(name='Basis')
            
        this_obj.shape_key_add(from_mix=False)   
        sk = this_obj.data.shape_keys.key_blocks[-1]
        sk.name = shape_name
        sk.value = 1
        shape_index = this_obj.data.shape_keys.key_blocks.keys().index(shape_name)
        bpy.context.object.active_shape_key_index = shape_index
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.context.tool_settings.transform_pivot_point = "CURSOR" 
        
        try:
            bpy.ops.object.vertex_group_set_active(group=vertex_groups_to_parse[0])
            bpy.ops.object.vertex_group_select()
            
            if transform_type == "RESIZE":
                if not is_version_4:
                    bpy.ops.transform.resize(override, value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.object.vertex_group_deselect()
                else:
                    bpy.ops.transform.resize(value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.object.vertex_group_deselect()
            elif transform_type == "TRANSLATE":
                if not is_version_4:
                    bpy.ops.transform.translate(override, value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.transform.resize(override, value=transformation_2)
                    bpy.ops.object.vertex_group_deselect()
                else:
                    bpy.ops.transform.translate(value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.transform.resize(override, value=transformation_2)
                    bpy.ops.object.vertex_group_deselect()                

        except:
            pass
        
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # REPEAT FOR SECOND BONE!
        
        bpy.context.view_layer.objects.active = head_bone_arm_target
        bpy.ops.object.mode_set(mode='EDIT')
        if use_eye_1:
            if " R " in vertex_groups_to_parse[1]:
                if right_eye_exists:
                    bpy.context.scene.cursor.location = (right_eye_1[0],right_eye_1[1],right_eye_1[2])
            elif " L " in vertex_groups_to_parse[1]:
                if left_eye_exists:
                    bpy.context.scene.cursor.location = (left_eye_1[0],left_eye_1[1],left_eye_1[2])
        else:
            if " R " in vertex_groups_to_parse[1]:
                if right_eye_exists:
                    bpy.context.scene.cursor.location = (right_eye_2[0],right_eye_2[1],right_eye_2[2])
            elif " L " in vertex_groups_to_parse[1]:
                if left_eye_exists:
                    bpy.context.scene.cursor.location = (left_eye_2[0],left_eye_2[1],left_eye_2[2])
                        
        # AFTER MOVING 3D CURSOR
        this_obj = bpy.data.objects.get(obj_get)
        bpy.context.view_layer.objects.active = this_obj
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT') 
        
        try:
            bpy.ops.object.vertex_group_set_active(group=vertex_groups_to_parse[1])
            bpy.ops.object.vertex_group_select()
            
            if transform_type == "RESIZE":
                if not is_version_4:
                    bpy.ops.transform.resize(override, value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.object.vertex_group_deselect()
                else:
                    bpy.ops.transform.resize(value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.object.vertex_group_deselect()                
            elif transform_type == "TRANSLATE":
                if not is_version_4:
                    bpy.ops.transform.translate(override, value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.transform.resize(override, value=transformation_2)
                    bpy.ops.object.vertex_group_deselect()
                else:
                    bpy.ops.transform.translate(value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.transform.resize(override, value=transformation_2)
                    bpy.ops.object.vertex_group_deselect()                
        except:
            pass
        
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # DONE
        sk.value = 0.0
        bpy.context.scene.cursor.location = (0.0,0.0,0.0)


    # Shape key to shrink pupils    
    create_shape_key2("Body", True, "pupils", "CURSOR", ["+EyeBone L A02","+EyeBone R A02"], "RESIZE", (0.5,0.5,0.5))
    # Shape keys to adjust eye during blink
    # For some reason, the math is different for v4, therefore adjust the nums so its more like v3.6
    if not is_version_4:
        create_shape_key("Body", False, "pupil-pushback-R", "CURSOR", ["+EyeBone R A02"], "TRANSLATE", (0, 0.00703, 0), (1.1,1.1,1.1),use_eye_1=True) # 0.0069, 70
        create_shape_key("Body", False, "pupil-pushback-L", "CURSOR", ["+EyeBone L A02"], "TRANSLATE", (0, 0.00703, 0), (1.1,1.1,1.1),use_eye_1=True)
    else:
        create_shape_key("Body", False, "pupil-pushback-R", "CURSOR", ["+EyeBone R A02"], "TRANSLATE", (0, 0.00234, 0), (1.1,1.1,1.1),use_eye_1=True) # 0.0069, 70
        create_shape_key("Body", False, "pupil-pushback-L", "CURSOR", ["+EyeBone L A02"], "TRANSLATE", (0, 0.00234, 0), (1.1,1.1,1.1),use_eye_1=True)    
    
    try:
        # Bring back EyeStar
        bpy.data.objects["EyeStar"].hide_set(False)
        bpy.data.objects["EyeStar"].hide_viewport = False
        bpy.data.objects["EyeStar"].hide_render = False

        # Shape key to enable EyeStar growth/shrinkage
        create_shape_key2("EyeStar", True, "EyeStar", "CURSOR", ["+EyeBone R A02","+EyeBone L A02"], "RESIZE", (0,0,0))
    except:
        pass

    bpy.context.tool_settings.transform_pivot_point = "MEDIAN_POINT"

    bpy.context.view_layer.objects.active = head_bone_arm_target
    bpy.ops.object.mode_set(mode='EDIT')

    if not toe_bones_exist:
        r_foot_bone = temp_armature.edit_bones["Bip001 R Foot"]
        r_foot_bone.tail = (-0.040187,-0.078244,0.005803) # X, Y, Z
        r_foot_bone.roll = 1.5708
        
        l_foot_bone = temp_armature.edit_bones["Bip001 L Foot"]
        l_foot_bone.tail = (0.040187,-0.078244,0.005803)
        l_foot_bone.roll =  1.5708

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = head_bone_arm_target

    # Let's let the RigUI script that poke made execute.

    context = bpy.context
    obj = context.object
    if obj.name[-4:] == ".001":
         obj.name = obj.name[:-4]
    print("New Run\n\n")
    ## Rename all bones in selected armature to ORG
    original_name = obj.name
    abadidea = {
        'Bip001 Pelvis': 'spine',
        'Bip001 L Thigh': 'thigh.L',
        'Bip001 L Calf': 'shin.L',
        'Bip001 L Foot': 'foot.L',
        'Bip001 L Toe0': 'toe.L',
        'Bip001 R Thigh': 'thigh.R',
        'Bip001 R Calf': 'shin.R',
        'Bip001 R Foot': 'foot.R',
        'Bip001 R Toe0': 'toe.R',
        'Bip001 Spine': 'spine.001',
        'Bip001 Spine1': 'spine.002',
        'Bip001 Spine2': 'spine.003',
        'Bip001 L Clavicle': 'shoulder.L',
        'Bip001 L UpperArm': 'upper_arm.L',
        'Bip001 L Forearm': 'forearm.L',
        'Bip001 L Hand': 'hand.L',
        'Bip001 L Finger0': 'thumb.01.L',
        'DMZ L 01': 'thumb.01.L',  ##WHERE DO THESE SIX COME FROM LMAO
        'DMZ L 02': 'thumb.02.L',
        'DMZ L 03': 'thumb.03.L',
        'DMZ R 01': 'thumb.01.R',
        'DMZ R 02': 'thumb.02.R',
        'DMZ R 03': 'thumb.03.R',    
        'Bip001 L Finger01': 'thumb.02.L',
        'Bip001 L Finger02': 'thumb.03.L',
        'Bip001 L Finger1': 'f_index.01.L',
        'Bip001 L Finger11': 'f_index.02.L',
        'Bip001 L Finger12': 'f_index.03.L',
        'Bip001 L Finger2': 'f_middle.01.L',
        'Bip001 L Finger21': 'f_middle.02.L',
        'Bip001 L Finger22': 'f_middle.03.L',
        'Bip001 L Finger3': 'f_ring.01.L',
        'Bip001 L Finger31': 'f_ring.02.L',
        'Bip001 L Finger32': 'f_ring.03.L',
        'Bip001 L Finger4': 'f_pinky.01.L',
        'Bip001 L Finger41': 'f_pinky.02.L',
        'Bip001 L Finger42': 'f_pinky.03.L',
        'Bip001 Neck': 'spine.004', #YO
        'Bip001 Head': 'spine.006', #RUHROH
        'Bip001 R Clavicle': 'shoulder.R',
        'Bip001 R UpperArm': 'upper_arm.R',
        'Bip001 R Forearm': 'forearm.R',
        'Bip001 R Hand': 'hand.R',
        'Bip001 R Finger0': 'thumb.01.R',
        'Bip001 R Finger01': 'thumb.02.R',
        'Bip001 R Finger02': 'thumb.03.R',
        'Bip001 R Finger1': 'f_index.01.R',
        'Bip001 R Finger11': 'f_index.02.R',
        'Bip001 R Finger12': 'f_index.03.R',
        'Bip001 R Finger2': 'f_middle.01.R',
        'Bip001 R Finger21': 'f_middle.02.R',
        'Bip001 R Finger22': 'f_middle.03.R',
        'Bip001 R Finger3': 'f_ring.01.R',
        'Bip001 R Finger31': 'f_ring.02.R',
        'Bip001 R Finger32': 'f_ring.03.R',
        'Bip001 R Finger4': 'f_pinky.01.R',
        'Bip001 R Finger41': 'f_pinky.02.R',
        'Bip001 R Finger42': 'f_pinky.03.R',
        '+EyeBone R A01': 'eye.R',
        '+EyeBone L A01': 'eye.L', 
        '+Breast L A01': 'breast.L',
        '+Breast R A01': 'breast.R', 
        }
    if not toe_bones_exist:
        del abadidea['Bip001 L Toe0']
        del abadidea['Bip001 R Toe0']

    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.context.selected_objects[0].data

    bpy.ops.armature.select_all(action='DESELECT')
    def select_bone(bone):
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        
    # Disconnect the eyes because it'll throw an error if I don't, disconnect the spines so the hip wiggle bone in the rigify rig works properly
    try:
        select_bone(armature.edit_bones["+EyeBone L A02"])
        select_bone(armature.edit_bones["+EyeBone R A02"])
    except:
        pass
    select_bone(armature.edit_bones["Bip001 Spine"])
    select_bone(armature.edit_bones["Bip001 Spine1"])
    select_bone(armature.edit_bones["Bip001 Spine2"])
    bpy.ops.armature.parent_clear(type='DISCONNECT')
    bpy.ops.armature.select_all(action='DESELECT')

    try:
        select_bone(armature.edit_bones["+Breast R A02"])
        select_bone(armature.edit_bones["+Breast L A02"])
        bpy.ops.armature.parent_clear(type='DISCONNECT')
        bpy.ops.armature.select_all(action='DESELECT')
    except:
        pass

    bones_list = obj.pose.bones
    for bone in bones_list:
        if bone.name in abadidea:
            bone.name = abadidea[bone.name]
    
    # Fix finger rolls - Thanks Poke!
    how_not = ['f_index.01.L', 'f_index.02.L', 'f_index.03.L']
    hahaha = ['f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L']
    to_name = ['f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L']
    things_efficiently = ['f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L']

    for bone in how_not:
        armature.edit_bones[bone].roll -= .1197
        
    for bone in hahaha:
        armature.edit_bones[bone].roll -= .04
        
    for bone in to_name:
        armature.edit_bones[bone].roll += .1297
        
    for bone in things_efficiently:
        armature.edit_bones[bone].roll += .338
    
    #Aw shit here we go again.  This second loop is for making it possible to symmetrize pose bones properly.
    for bone in bones_list:
        if ".L" in bone.name: 
            whee = bone.name[:-2] + ".R"
            if "f_" in bone.name or "thumb" in bone.name:
                armature.edit_bones[whee].roll = -armature.edit_bones[bone.name].roll
            else:
                armature.edit_bones[bone.name].roll = -armature.edit_bones[whee].roll

    armature.edit_bones["shoulder.L"].roll += 3.14
    armature.edit_bones["shoulder.R"].roll -= 3.14  

    
    
    # Fixes the thumb scale rotating inward on x instead of z
    armature.edit_bones["thumb.01.L"].roll += 3.14 / 4
    armature.edit_bones["thumb.02.L"].roll += 3.14 / 4
    armature.edit_bones["thumb.03.L"].roll += 3.14 / 4     
    armature.edit_bones["thumb.01.R"].roll -= 3.14 / 4
    armature.edit_bones["thumb.02.R"].roll -= 3.14 / 4
    armature.edit_bones["thumb.03.R"].roll -= 3.14 / 4 

                                    
                                                                                                                                
    for bone in armature.edit_bones:
        if "thumb" in bone.name or "index" in bone.name or "middle" in bone.name or "ring" in bone.name or "pinky" in bone.name:
            if ".L" in bone.name:
                armature.edit_bones[bone.name].roll -= 1.571 
            else:
                armature.edit_bones[bone.name].roll += 1.571 
        ## Not sure why this bone exist but it's gotta go lmao                                                      
        if bone.name == "Bip001": 
            for childbone in bone.children:
                if childbone.name != "spine":
                    armature.edit_bones[childbone.name].parent = armature.edit_bones['spine'] 
            armature.edit_bones.remove(bone)
        elif ".L" not in bone.name and ".R" not in bone.name:
            armature.edit_bones[bone.name].roll = 0

            
    ## Fixes the weirdass pelvis/spine bone.  Sets the spine's head and tail X to 0.  
    def realign(bone):
        bone.head.x = 0
        bone.tail.x = 0
    realign(armature.edit_bones['spine'])
    realign(armature.edit_bones['spine.006'])


    ## Attaches the feet to the toes and the upperarms to lowerarms
    def attachfeets(foot, toe):
        armature.edit_bones[foot].tail.x = armature.edit_bones[toe].head.x
        armature.edit_bones[foot].tail.y = armature.edit_bones[toe].head.y
        armature.edit_bones[foot].tail.z = armature.edit_bones[toe].head.z

    if toe_bones_exist:
        attachfeets('foot.L', 'toe.L')
        attachfeets('foot.R', 'toe.R')
        
    attachfeets('upper_arm.L', 'forearm.L')
    attachfeets('upper_arm.R', 'forearm.R')
    attachfeets('thigh.L', 'shin.L')
    attachfeets('thigh.R', 'shin.R') 
    attachfeets('forearm.L', 'hand.L')
    attachfeets('forearm.R', 'hand.R')
    attachfeets('spine', 'spine.001')
    attachfeets('spine.001', 'spine.002')
    attachfeets('spine.002', 'spine.003')
    attachfeets('spine.003', 'spine.004')
    attachfeets('spine.004', 'spine.006')

    ## Points toe bones in correct direction
    if toe_bones_exist:
        armature.edit_bones['toe.L'].tail.z = 0
        armature.edit_bones['toe.L'].tail.y -= 0.05

        armature.edit_bones['toe.R'].tail.z = 0
        armature.edit_bones['toe.R'].tail.y -= 0.05
            
    bpy.ops.armature.select_all(action='DESELECT')
    try:
        select_bone(armature.edit_bones["breast.L"])
        bpy.ops.armature.symmetrize()
        bpy.ops.armature.select_all(action='DESELECT')

    except Exception:
        pass

    try:
        armature.edit_bones["eye.L"].name = "DEF-eye.L"
        armature.edit_bones["eye.R"].name = "DEF-eye.R"
    except:
        pass

    bpy.ops.object.mode_set(mode='POSE')

    bpy.ops.object.expykit_convert_bone_names(src_preset='Rigify_Metarig.py', trg_preset='Rigify_Deform.py')
    bpy.ops.object.expykit_extract_metarig(rig_preset='Rigify_Metarig.py', assign_metarig=True)



    ## Fixes the tiddy bones.  Expykit, why did you neglect them

    metarm = bpy.data.objects["metarig"].data
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.data.objects[obj.name].data

    ## Left side first, right side's xyz is same as left, but x is negative
    def getboob(bone, tip):
        if tip == "head":
            return armature.edit_bones[bone].head.x, armature.edit_bones[bone].head.y, armature.edit_bones[bone].head.z
        else:
            return armature.edit_bones[bone].tail.x, armature.edit_bones[bone].tail.y, armature.edit_bones[bone].tail.z
            
        
    try:
        xh, yh, zh = getboob("breast.L", "head")
        xt, yt, zt = getboob("breast.L", "tail")

        ## Change the meta arm's boob positions

        def fixboob(bone, xh, yh, zh, xt, yt, zt):
            bone.head.x = xh
            bone.head.y = yh
            bone.head.z = zh
            bone.tail.x = xt
            bone.tail.y = yt
            bone.tail.z = zt

        boobL = metarm.edit_bones["breast.L"]
        fixboob(boobL, xh, yh, zh, xt, yt, zt)
        boobR = metarm.edit_bones["breast.R"]
        fixboob(boobR, -xh, yh, zh, -xt, yt, zt)

        boobL.roll = armature.edit_bones["breast.L"].roll
        boobR.roll = -boobL.roll
    except Exception:
        # If breast bones dont exist in the orig rig, then delete from the meta rig
        metarm.edit_bones.remove(metarm.edit_bones["breast.L"])
        metarm.edit_bones.remove(metarm.edit_bones["breast.R"])
        


    # Fixes the finger rolls
    bpy.ops.object.mode_set(mode='OBJECT')
    metapose = bpy.data.objects['metarig'].pose
    for bone_name in ['f_index', 'f_middle', 'f_ring', 'f_pinky']:
        metapose.bones[f"{bone_name}.01.L"].rigify_parameters.primary_rotation_axis = 'Z'
        metapose.bones[f"{bone_name}.01.R"].rigify_parameters.primary_rotation_axis = '-Z'
                                                                               
    metapose.bones["thumb.01.L"].rigify_parameters.primary_rotation_axis = 'Z'
    metapose.bones["thumb.01.R"].rigify_parameters.primary_rotation_axis = '-Z'                                                                               
                                          

    ## This part corrects metarm finger rolls
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    armature = obj.data

    for o in bpy.data.objects:
        # Check for given object names
        if o.name in ("metarig", armature.name):
            o.select_set(True)


    bpy.ops.object.mode_set(mode='EDIT')
    for bone in metarm.edit_bones:
        if "f_" in bone.name or "thumb" in bone.name:
            bone.roll =  armature.edit_bones["DEF-"+bone.name].roll

    # Fix hand bones being rotated 90 degrees sideways and arm deformation bones being wonky
    if "Loli" in obj.name:
        metarm.edit_bones["upper_arm.L"].tail.y += .003
        metarm.edit_bones["upper_arm.R"].tail.y += .003

    ##########  DETACH PHYSICS BONES,  

    metanames = ['eye.L', 'eye.R', 'spine', 'thigh.L', 'shin.L', 'foot.L', 'toe.L', 'thigh.R', 'shin.R', 'foot.R', 'toe.R', 'spine.001', 'spine.002', 'spine.003', 'breast.L', 'breast.R', 'shoulder.L', 'upper_arm.L', 'forearm.L', 'hand.L', 'thumb.01.L', 'thumb.02.L', 'thumb.03.L', 'f_index.01.L', 'f_index.02.L', 'f_index.03.L', 'f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L', 'f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L', 'f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L', 'spine.004', 'spine.006', 'shoulder.R', 'upper_arm.R', 'forearm.R', 'hand.R', 'thumb.01.R', 'thumb.02.R', 'thumb.03.R', 'f_index.01.R', 'f_index.02.R', 'f_index.03.R', 'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R', 'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R', 'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R']
    if not toe_bones_exist:
        metanames.remove("toe.L")
        metanames.remove("toe.R")


    pre_res = ["DEF-" + bonename for bonename in metanames]
    armature = obj.data ## Original char rig


    ## Make a dictionary.  Key is a main body bone that exists in the Rigify (arm, leg, spine, etc), and the value is a list of all the children bones that aren't other main body bones (usually hair, clothes, deform, etc.)
    savethechildren = {
        
    }
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in armature.edit_bones:
        if bone.name in pre_res:
            childlist = []
            for childbone in armature.edit_bones[bone.name].children:
                if childbone.name not in pre_res: # Adds only non-main body bones, avoids like forearm or knee etc
                    childlist.append(childbone.name)
            if childlist: # If list isn't empty, add it to dict
                wtf = bone.name
                savethechildren[wtf] = childlist

        
    ## Duplicates the physics bones
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    bones = armature.edit_bones[:]
    for bone in bones:
        if bone.name not in pre_res:
            #this is a physics bone, so duplicate it.
            bone.select = True
            bone.select_tail = True
            bone.select_head = True

    bpy.ops.armature.separate()
    # Generates rigify rig and renames it to 'rigify'
    bpy.ops.pose.rigify_generate()
    bpy.data.objects[obj.name].name = "rigify"
    bpy.context.view_layer.objects.active = bpy.data.objects[armature.name + ".001"]


    for o in bpy.data.objects:
        # Check for given object names
        if o.name in ("rigify", armature.name):
            o.select_set(True)
            
    # THEN REATTACH PHYSICS

    bpy.ops.object.mode_set(mode='OBJECT')
    ### BLENDER ARE U GOOD LMAO WTF IS THIS (this joins two objects together)
    newrig = armature.name + ".001" ## New temporary armature with the physics bones. Hopefully you didnt touch any names lmao

    ## Why's the list for selected objects ordered alphabetically instead of by selection order
    objList = bpy.context.selected_objects
    unselected = [obj for obj in objList if obj != context.active_object]
    rigifyr = unselected[0]  ## Rigified Rig

    obs = [bpy.data.objects.get("rigify"), bpy.data.objects.get(newrig)]
    c={}
    c["object"] = c["active_object"] = bpy.data.objects.get("rigify")
    c["selected_objects"] = c["selected_editable_objects"] = obs
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    
    with bpy.context.temp_override(active_object=bpy.data.objects.get("rigify"), selected_editable_objects=obs):
        bpy.ops.object.join()


    bpy.context.view_layer.objects.active = bpy.data.objects["rigify"]

    setup_neck_and_head_follow(neck_follow_value=1.0, head_follow_value=1.0)
    setup_finger_scale_controls_on_x_axis_to_curl_just_the_fingertips(rigifyr)

    bpy.ops.object.mode_set(mode='EDIT')

    #### whats this for???
    #oh i think it's useless now bc there's only one rig LMAOLMAO
    #for bone in bones_list:
    #    armature.edit_bones[bone.name].roll = rigifyr.data.edit_bones[bone.name].roll
    ####

    ## Reattach the physics bones to their parents
    #Go back into rigify, find the main body bones, and reattach every bone in the corresponding dict list
    for mainbone in savethechildren:    
        for childbone in savethechildren[mainbone]:
            rigifyr.data.edit_bones[childbone].parent = rigifyr.data.edit_bones[mainbone]

    print("donelol\n")
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects["rigify"].show_in_front = True

    # Symmetrize clothes/hair bones
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in rigifyr.data.edit_bones:
        if " L " in bone.name:  # Finds clothes/hair bones with symmetrical bones
            y = bone.name.find(' L ')  # Finds index of "Hair L 1"
            orgname = bone.name
            try:
                oppbone = orgname[:y] + " R " + orgname[y+3:] # oppbone = "Hair R 1"
                bone.name = orgname[:y] + orgname[y+3:] + ".L"  #Rename bones to "Hair 1.L/R" so Blender 
                rigifyr.data.edit_bones[oppbone].name = orgname[:y] + orgname[y+3:] + ".R" # goes ":o symmetry"
            except:
                pass

    rigifyr.pose.bones["upper_arm_parent.L"]["pole_parent"] = 2
    rigifyr.pose.bones["upper_arm_parent.R"]["pole_parent"] = 2
    rigifyr.pose.bones["thigh_parent.L"]["pole_parent"] = 2
    rigifyr.pose.bones["thigh_parent.R"]["pole_parent"] = 2

    bpy.ops.object.mode_set(mode='OBJECT')
    #change active object to rigifyr

    bpy.context.view_layer.objects.active = bpy.data.objects["rigify"]

    bpy.ops.object.mode_set(mode='OBJECT')

    # This part puts all the main bones I use into the secoond bone layer
    listofbones = ["root", "foot_heel_ik.R", "foot_heel_ik.L", "toe_ik.R", "toe_ik.L", "foot_ik.R", "foot_ik.L", "thigh_ik_target.R", "thigh_ik_target.L", "hips", "torso", "chest", "neck", "head", "shoulder.L", "shoulder.R", "upper_arm_fk.L", "upper_arm_fk.R", "forearm_fk.L", "forearm_fk.R", "hand_fk.L", "hand_fk.R", "upper_arm_ik_target.L", "upper_arm_ik_target.R", "hand_ik.R", "hand_ik.L", ]

    if not toe_bones_exist:
        listofbones.remove("toe_ik.R")
        listofbones.remove("toe_ik.L")
        
    if not is_version_4:
        for bone in listofbones:
            bpy.context.active_object.pose.bones[bone].bone.layers[1] = True
        
    try:
        bpy.data.objects["EyeStar"].hide_viewport = False
    except:
        pass

    x = original_name.split("_")
    char_name = x[-1]
    bpy.data.objects["rigify"].name = char_name + "Rig"
                
    bpy.ops.object.mode_set(mode='POSE')   
    bpy.ops.pose.select_all(action='DESELECT')
    bones_list = obj.pose.bones

    # Creates selection sets for FK arms + shoulders, hair bones, and clothes bones.  Selection Sets is an addon that comes with Blender.
    try:
        bpy.ops.object.mode_set(mode='POSE')

        arms = ['upper_arm_fk', 'forearm_fk', 'hand_fk', 'shoulder']
        bpy.ops.pose.select_all(action='DESELECT')
        for side in ['.L', '.R']:
            for bone in arms:
                bonename = bone + side
                rigifyr.pose.bones[bonename].bone.select= True
        bpy.ops.pose.selection_set_add()
        bpy.ops.pose.selection_set_assign()
        bpy.ops.pose.select_all(action='DESELECT')

        ## Hair
        for bone in bones_list:
            if "Hair" in bone.name:
                rigifyr.pose.bones[bone.name].bone.select = True
        bpy.ops.pose.selection_set_add()
        bpy.ops.pose.selection_set_assign()
        bpy.ops.pose.select_all(action='DESELECT')

        ## Clothes
        for bone in bones_list:
            if "Amice" in bone.name or ("fk" not in bone.name and "tweak" not in bone.name and "Twist" not in bone.name and "Hair" not in bone.name and (bone.name[-1].isdigit() or bone.name[-3].isdigit())):
                rigifyr.pose.bones[bone.name].bone.select = True
        bpy.ops.pose.selection_set_add()
        bpy.ops.pose.selection_set_assign()
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.context.object.selection_sets[0].name = "FK Arms"
        bpy.context.object.selection_sets[1].name = "Hair"
        bpy.context.object.selection_sets[2].name = "Clothes...and teeth and eyes lmao"
    except:
        pass
    
    # Fix scaling for finger tips.
    rig = bpy.context.object

    for oDrv in rig.animation_data.drivers:
        for variable in oDrv.driver.variables:
            for target in variable.targets:
                if ".03" in oDrv.data_path and target.data_path[-7:] == "scale.y":
                    target.data_path = target.data_path[:-1] + "x"

    fingerlist = ["thumb.01_master", "f_index.01_master", "f_middle.01_master", "f_ring.01_master", "f_pinky.01_master"]

    for side in [".L", ".R"]:
        for bone in fingerlist:
            rig.pose.bones[bone + side].lock_scale[0] = False

    # Fix face shading being offset 90 degrees
    bpy.ops.object.mode_set(mode='OBJECT')
    try:
        head_driver_obj = bpy.data.objects.get("Head Driver") or bpy.data.objects.get("Head Origin")
        bpy.context.view_layer.objects.active = head_driver_obj
        bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='OBJECT')
    except:
        pass

    # POST RIGIFY SCRIPT EXECUTION ----------------->

    # Hide metarig (I think you can actually delete it instead?)
    bpy.data.objects["metarig"].hide_select = True
    bpy.data.objects["metarig"].hide_viewport = True
    bpy.data.objects["metarig"].hide_render = True

    # Moves specified param and it's children into the collection
    def move_into_collection(object,collection,include_children=True):
        
        # Get object
        this_obj = bpy.context.scene.objects.get(object)
        # Get existing collection or make new one
        this_coll = bpy.data.collections.get(collection)
        if not this_coll:
            this_coll = bpy.data.collections.new(collection)
            bpy.context.scene.collection.children.link(this_coll)
            
        # Move object into collection
        if this_obj:
            # Unlink it from all previous collections before moving it to new one
            for coll in this_obj.users_collection:
                coll.objects.unlink(this_obj)
                
            # Move it to our specified collection (This only does the parent obj)
            this_coll.objects.link(this_obj)
            
            if include_children:
                # Now we move the children of this object
                for child_obj in this_obj.children:
                    # Same thing, unlink previous collections
                    for coll in child_obj.users_collection:
                        coll.objects.unlink(child_obj)
                    this_coll.objects.link(child_obj)
                
    # Move the rig into the char name's collection                        
    move_into_collection(char_name+"Rig",char_name)

    # Let's make a new wgt collection inside the char coll.
    char_coll = bpy.data.collections.get(char_name)
    wgt_coll = bpy.data.collections.new("wgt")
    char_coll.children.link(wgt_coll)

    # Rename our WGT collection and put the metarig into it.
    for coll in bpy.data.collections:
        if coll.name.startswith("WGTS"):
            coll.name = "WG"

    move_into_collection("metarig","wgt")


    # Unlink all inner objects from the old WGT collection. We want them inside the new one.
    for obj in bpy.data.objects:
        if obj.name.startswith("WGT"):
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            
            wgt_coll.objects.link(obj)
            
    # Remove old unused wgt collection                
    bpy.data.collections.remove(bpy.data.collections.get("WG"))

    # Obfuscate light driving stuff not needed, keep the main light.        
    move_into_collection("Face Light Direction","wgt")
    move_into_collection("Head Driver",char_name)
    move_into_collection("Main Light Direction",char_name)

    # V3 Shader Support - New empty names
    move_into_collection("Head Origin",char_name)
    move_into_collection("Light Direction",char_name)

    bpy.data.collections["wgt"].hide_select = True
    bpy.data.collections["wgt"].hide_viewport = True
    bpy.data.collections["wgt"].hide_render = True

    head_driver_obj = bpy.data.objects.get("Head Driver") or bpy.data.objects.get("Head Origin")
    if head_driver_obj:
        head_driver_obj.hide_select = True
        head_driver_obj.hide_viewport = True
        head_driver_obj.hide_render = True

    head_forward_obj = bpy.data.objects.get("Head Forward")
    head_forward_obj.hide_select = True
    head_forward_obj.hide_viewport = True
    head_forward_obj.hide_render = True

    head_up_obj = bpy.data.objects.get("Head Up")
    head_up_obj.hide_select = True
    head_up_obj.hide_viewport = True
    head_up_obj.hide_render = True

    # IMPORTANT: This must be done before deleting the "Collection" collection in case Lighting Panel gets appended in there
    # remove lighting colls - also move the RGB wheels into the rig obj
    lighting_panel_rig_obj = bpy.data.objects.get(LightingPanelNames.Objects.LIGHTING_PANEL)
    if lighting_panel_rig_obj:
        to_del_coll = bpy.data.collections.get(LightingPanelNames.Collections.WIDGET_COLLECTION)
        for obj in to_del_coll.objects:
            move_into_collection(obj.name, "wgt")
        to_del_coll = bpy.data.collections.get(LightingPanelNames.Collections.PICKER)
        for obj in to_del_coll.objects:
            move_into_collection(obj.name, "wgt")
        to_del_coll = bpy.data.collections.get(LightingPanelNames.Collections.WHEEL)
        for obj in to_del_coll.objects:
            move_into_collection(obj.name, char_name)
        # DO NOT INCLUDE CHILDREN. This will cause ColorPickers to be moved into the rig object.
        move_into_collection(LightingPanelNames.Objects.LIGHTING_PANEL, char_name, include_children=False)
        bpy.data.collections.remove(bpy.data.collections.get(LightingPanelNames.Collections.LIGHTING_PANEL), do_unlink=True)

    # If it exists, gets rid of the default collection.
    camera_coll = bpy.data.collections.get("Collection")
    if camera_coll:
        bpy.data.collections.remove(camera_coll,do_unlink=True)

    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = searchForLayerCollection(layer_collection, "wgt")
    bpy.context.view_layer.active_layer_collection = layerColl

    layerColl.exclude = True

    # Make our lives easier, display the bones as sticks and make sure we can view from front.    
    bpy.data.armatures[original_name].display_type = 'STICK'
    bpy.data.objects[char_name+"Rig"].show_in_front = True

    # Going into pose mode with our character selected.
    bpy.ops.object.select_all(action='DESELECT')
    our_char =  bpy.data.objects.get(char_name+"Rig")
    if our_char:
        our_char.select_set(True)
        bpy.context.view_layer.objects.active = our_char
        
        bpy.ops.object.mode_set(mode='POSE')

    # Function to automatically move a bone (if it exists) to the specified bone layer. pass in num+1 than layer desired.        
    def move_bone(bone_name,to_layers):
        armature =  bpy.context.active_object
        armature_data = armature.data
        
        if bone_name in armature_data.bones:
            bone = armature_data.bones[bone_name]
            
            for i in range(32):
                bone.layers[i] = False
            
            to_layers = [to_layers] if isinstance(to_layers, int) else to_layers
            
            for layer in to_layers:
                bone.layers[layer] = True
                print("enabling layer: " + str(layer) + " for " + bone_name)
            


    if not is_version_4:
        # Put away every other bone to the physics layer (22)
        for bone in bpy.context.active_object.data.bones:
            if bone.layers[0]:  # Check if the bone is on layer face
                move_bone(bone.name, 25)  # Move the bone to layer 23
            
    # Let's append our root_shape custom bones
    path_to_file = file_path + "/Collection"

    # Bring in our collections: root shapes, face rig, and the eye rig
    bpy.ops.wm.append(filename='append_Face Plate', directory=path_to_file)

    bpy.ops.wm.append(filename='append_Root', directory=path_to_file)

    bpy.ops.wm.append(filename='append_Eyes', directory=path_to_file)
    
    bpy.ops.wm.append(filename='append_Pelvis', directory=path_to_file)
    
    bpy.ops.wm.append(filename='append_Foot', directory=path_to_file)
    
    bpy.ops.wm.append(filename='append_Hand', directory=path_to_file)
    
    bpy.ops.wm.append(filename='append_Props', directory=path_to_file)

    this_obj = None
    for obj in bpy.data.objects:
        if "Rig" in obj.name:
            this_obj = obj

    this_obj.pose.bones["root"].custom_shape = bpy.data.objects["root plate.002"]
    this_obj.pose.bones["root"].use_custom_shape_bone_size = False
    
    this_obj.pose.bones["head"].custom_shape_scale_xyz = (1.65,1.65,1.65)
    this_obj.pose.bones["head"].custom_shape = bpy.data.objects["neck"]
    this_obj.pose.bones["head"].custom_shape_translation = (0.0,0.255,0.0)
    this_obj.pose.bones["head"].custom_shape_rotation_euler[0] = 1.5708
    this_obj.pose.bones["head"].use_custom_shape_bone_size = False
    
    this_obj.pose.bones["neck"].use_custom_shape_bone_size = False
    this_obj.pose.bones["neck"].custom_shape = bpy.data.objects["neck"]
    this_obj.pose.bones["neck"].custom_shape_scale_xyz = (1,1,1)
    this_obj.pose.bones["neck"].custom_shape_translation = (0.0,0.035,0.007)
    this_obj.pose.bones["neck"].custom_shape_rotation_euler[0] = 1.5708
    
    this_obj.pose.bones["foot_ik.L"].use_custom_shape_bone_size = False
    this_obj.pose.bones["foot_ik.R"].use_custom_shape_bone_size = False
    this_obj.pose.bones["foot_ik.L"].custom_shape = bpy.data.objects["foot1"]
    this_obj.pose.bones["foot_ik.R"].custom_shape = bpy.data.objects["foot1"]

    this_obj.pose.bones["thigh_ik_target.L"].custom_shape = bpy.data.objects["primo-joint"]
    this_obj.pose.bones["thigh_ik_target.R"].custom_shape = bpy.data.objects["primo-joint"]
    this_obj.pose.bones["upper_arm_ik_target.R"].custom_shape = bpy.data.objects["primo-joint"]
    this_obj.pose.bones["upper_arm_ik_target.L"].custom_shape = bpy.data.objects["primo-joint"]

    this_obj.pose.bones["thigh_ik_target.L"].custom_shape_scale_xyz[0] = 0.75
    this_obj.pose.bones["thigh_ik_target.L"].custom_shape_scale_xyz[1] = 0.75
    this_obj.pose.bones["thigh_ik_target.L"].custom_shape_scale_xyz[2] = 0.75
    this_obj.pose.bones["thigh_ik_target.R"].custom_shape_scale_xyz[0] = 0.75
    this_obj.pose.bones["thigh_ik_target.R"].custom_shape_scale_xyz[1] = 0.75
    this_obj.pose.bones["thigh_ik_target.R"].custom_shape_scale_xyz[2] = 0.75

    this_obj.pose.bones["torso"].custom_shape = bpy.data.objects["pelvis2"]
    this_obj.pose.bones["torso"].use_custom_shape_bone_size = False
  
    this_obj.pose.bones["hips"].custom_shape = bpy.data.objects["hips"]
    this_obj.pose.bones["hips"].custom_shape_scale_xyz = (1,1,1)
    this_obj.pose.bones["hips"].custom_shape_translation = (0.0,-0.04,0.044)
    this_obj.pose.bones["hips"].custom_shape_rotation_euler[0] = 1.309
    this_obj.pose.bones["hips"].use_custom_shape_bone_size = False
    
    this_obj.pose.bones["chest"].custom_shape = bpy.data.objects["chest"]
    this_obj.pose.bones["chest"].custom_shape_scale_xyz = (0.6,0.6,0.6)
    this_obj.pose.bones["chest"].custom_shape_translation = (0.0,0.18,0.0)
    this_obj.pose.bones["chest"].custom_shape_rotation_euler[0] = 1.5708
    this_obj.pose.bones["chest"].use_custom_shape_bone_size = False
    
    this_obj.pose.bones["shoulder.L"].custom_shape_scale_xyz = (1.6,1.6,1.6)
    this_obj.pose.bones["shoulder.R"].custom_shape_scale_xyz = (1.6,1.6,1.6)

    this_obj.pose.bones["foot_heel_ik.L"].custom_shape_translation = (0.0,0.06,0.0)
    this_obj.pose.bones["foot_heel_ik.R"].custom_shape_translation = (0.0,0.06,0.0)

    this_obj.pose.bones["foot_spin_ik.R"].custom_shape_translation = (0.0,-0.05,0.02)
    this_obj.pose.bones["foot_spin_ik.L"].custom_shape_translation = (0.0,-0.05,0.02)

    this_obj.pose.bones["toe_ik.L"].custom_shape_translation = (0.0,0.06,0.00)
    this_obj.pose.bones["toe_ik.R"].custom_shape_translation = (0.0,0.06,0.00)
    this_obj.pose.bones["toe_ik.L"].custom_shape_scale_xyz = (0.781,0.781,0.350)
    this_obj.pose.bones["toe_ik.R"].custom_shape_scale_xyz = (0.781,0.781,0.350)

    this_obj.pose.bones["hand_ik.R"].use_custom_shape_bone_size = False
    this_obj.pose.bones["hand_ik.R"].custom_shape = bpy.data.objects["wrist"]
    
    this_obj.pose.bones["hand_ik.L"].use_custom_shape_bone_size = False
    this_obj.pose.bones["hand_ik.L"].custom_shape = bpy.data.objects["wrist"]

    this_obj.pose.bones["palm.L"].custom_shape_scale_xyz = (1.2,1.2,1.2)
    this_obj.pose.bones["palm.R"].custom_shape_scale_xyz = (1.2,1.2,1.2)
    

    # Merge the armatures; go into object mode and make sure nothing is selected
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    # Select custom face armature
    face_rig_obj = bpy.data.objects.get("facerig")
    if face_rig_obj:
        face_rig_obj.select_set(True)

    # Select lighting panel armature
    lighting_panel_rig_obj = bpy.data.objects.get(LightingPanelNames.Objects.LIGHTING_PANEL)
    if lighting_panel_rig_obj:
        lighting_panel_rig_obj.select_set(True)

    # Select eye rig    
    eye_rig_obj = bpy.data.objects.get("eyerig")
    if eye_rig_obj:
        eye_rig_obj.select_set(True)
    
    # Select root rig    
    root_rig_obj = bpy.data.objects.get("rootrig")
    if root_rig_obj:
        root_rig_obj.select_set(True)
        
    # Select pelvis rig    
    pelvis_rig_obj = bpy.data.objects.get("pelvisrig")
    if pelvis_rig_obj:
        pelvis_rig_obj.select_set(True)
        
    # Select foot L rig    
    foot_l_rig_obj = bpy.data.objects.get("footrig-L")
    if foot_l_rig_obj:
        foot_l_rig_obj.select_set(True)
        
    # Select foot R rig    
    foot_r_rig_obj = bpy.data.objects.get("footrig-R")
    if foot_r_rig_obj:
        foot_r_rig_obj.select_set(True)
        
    # Select hand R rig    
    hand_r_rig_obj = bpy.data.objects.get("handrig-R")
    if hand_r_rig_obj:
        hand_r_rig_obj.select_set(True)
        
    # Select hand L rig    
    hand_l_rig_obj = bpy.data.objects.get("handrig-L")
    if hand_l_rig_obj:
        hand_l_rig_obj.select_set(True)
        
    # Select prop rig   
    prop_rig_obj = bpy.data.objects.get("prop-rig")
    if prop_rig_obj:
        prop_rig_obj.select_set(True)
            
    # Select char armature
    if our_char:
        our_char.select_set(True)

    # Join them
    bpy.ops.object.join()
     
    # We want to save all the VG names here, perhaps we can use them to identify weighted def bones.  
    bpy.context.view_layer.objects.active = bpy.data.objects.get("Body")    
    vertex_groups_list = [vg.name for vg in bpy.context.object.vertex_groups]
    bpy.context.view_layer.objects.active = head_bone_arm_target
    
    # Get the intersection point of a line with a perpendicular plane
    def project_line_in_space(points1, points2, axis):
        x1, y1, z1 = points1
        x2, y2, z2 = points2

        m = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else None
        b = y1 - m * x1 if m is not None else None

        if m is None:
            return None

        # Intersection point
        intersection_x = axis
        intersection_y = m * intersection_x + b
        intersection_z = z1 + (intersection_y - y1) * (z2 - z1) / (y2 - y1)

        intersection_point = (intersection_x, intersection_y, intersection_z)
        return intersection_point

    # Select the object then access it's rig (its obj data)
    ob = bpy.data.objects[char_name+"Rig"]
    armature = ob.data

    # In edit mode, select platebone and head controller and set their parent bones.
    bpy.ops.object.mode_set(mode='EDIT')
    armature.edit_bones['plate-border'].parent = armature.edit_bones['head']
    armature.edit_bones['plate-settings'].parent = armature.edit_bones['head']
    if armature.edit_bones.get(LightingPanelNames.Bones.LIGHTING_PANEL):
        armature.edit_bones[LightingPanelNames.Bones.LIGHTING_PANEL].parent = armature.edit_bones['head']
    
    armature.edit_bones['plate-border'].head = armature.edit_bones['neck'].head.copy()
    armature.edit_bones['plate-border'].tail = armature.edit_bones['neck'].tail.copy()
    armature.edit_bones['plate-border'].head.x = 0.33
    armature.edit_bones['plate-border'].head.y = 0
    armature.edit_bones['plate-border'].tail.y = 0
    armature.edit_bones['plate-border'].tail.x = 0.33
    
    armature.edit_bones['plate-settings'].head = armature.edit_bones['head'].head.copy()
    armature.edit_bones['plate-settings'].tail = armature.edit_bones['head'].head.copy()
    armature.edit_bones['plate-settings'].head.y = 0
    armature.edit_bones['plate-settings'].tail.y = 0
    armature.edit_bones['plate-settings'].head.z += 0.5
    armature.edit_bones['plate-settings'].tail.z += 0.6
    
    # While here, set inherit scales as needed.
    armature.edit_bones['upper_arm_parent.L'].inherit_scale="NONE"
    armature.edit_bones['upper_arm_parent.R'].inherit_scale="NONE"
    armature.edit_bones['thigh_parent.L'].inherit_scale="NONE"
    armature.edit_bones['thigh_parent.R'].inherit_scale="NONE"
    armature.edit_bones['torso-outer'].inherit_scale="AVERAGE"
    armature.edit_bones['torso-inner'].inherit_scale="FULL"
    armature.edit_bones['torso'].inherit_scale="FULL"
    # fix the bad rolls of the torso bone
    armature.edit_bones['torso'].roll = 0
    armature.edit_bones['torso-inner'].roll = 0
    armature.edit_bones['torso-outer'].roll = 0
    
    armature.edit_bones['forearm_tweak-pin.R'].inherit_scale="AVERAGE"
    armature.edit_bones['forearm_tweak-pin.L'].inherit_scale="AVERAGE"
    armature.edit_bones['shin_tweak-pin.L'].inherit_scale="AVERAGE"
    armature.edit_bones['shin_tweak-pin.R'].inherit_scale="AVERAGE"
    armature.edit_bones['hand-ik-L'].inherit_scale="AVERAGE"
    armature.edit_bones['hand-ik-R'].inherit_scale="AVERAGE"
    armature.edit_bones['hand_ik.L'].inherit_scale="FULL"
    armature.edit_bones['hand_ik.R'].inherit_scale="FULL"
           
    # Fixing Foot spin bone pos for chars with generated feet bones.
    if not toe_bones_exist:
        armature.edit_bones['foot_spin_ik.L'].head.z = 0
        armature.edit_bones['foot_spin_ik.L'].tail.z = 0
        
        armature.edit_bones['foot_spin_ik.R'].head.z = 0
        armature.edit_bones['foot_spin_ik.R'].tail.z = 0
    
    # SET RELATIONSHIPS as needed after bringing in new bones  
    armature.edit_bones['root'].parent = armature.edit_bones['root-inner']
    
    armature.edit_bones['torso-outer'].parent = armature.edit_bones['MCH-torso.parent']
    armature.edit_bones['torso'].parent = armature.edit_bones['torso-inner']
    armature.edit_bones['torso_pivot.002'].parent = armature.edit_bones['torso']
    armature.edit_bones['hips'].parent = armature.edit_bones['MCH-torso_pivot.002']
    armature.edit_bones['chest'].parent = armature.edit_bones['MCH-torso_pivot.002']
    armature.edit_bones['MCH-spine.001'].parent = armature.edit_bones['MCH-torso_pivot.002']
    armature.edit_bones['MCH-spine.002'].parent = armature.edit_bones['MCH-torso_pivot.002']
    
    armature.edit_bones['ik-pivot-L'].parent = armature.edit_bones['foot_ik.L']    
    armature.edit_bones['ik-pivot-R'].parent = armature.edit_bones['foot_ik.R']    
    armature.edit_bones['foot_spin_ik.L'].parent = armature.edit_bones['ik-target-L']    
    armature.edit_bones['foot_spin_ik.R'].parent = armature.edit_bones['ik-target-R']   

    armature.edit_bones['hand-ik-L'].parent = armature.edit_bones['MCH-hand_ik.parent.L']    
    armature.edit_bones['hand-ik-R'].parent = armature.edit_bones['MCH-hand_ik.parent.R']    
    armature.edit_bones['hand_ik.L'].parent = armature.edit_bones['mch-hand-ik-pivot-L']
    armature.edit_bones['hand_ik.R'].parent = armature.edit_bones['mch-hand-ik-pivot-R']    
    armature.edit_bones['mch-hand-ik-wrist-L'].parent = armature.edit_bones['hand_ik.L']    
    armature.edit_bones['mch-hand-ik-wrist-R'].parent = armature.edit_bones['hand_ik.R']    
    armature.edit_bones['MCH-upper_arm_ik_target.L'].parent = armature.edit_bones['mch-hand-ik-wrist-L']    
    armature.edit_bones['MCH-upper_arm_ik_target.R'].parent = armature.edit_bones['mch-hand-ik-wrist-R']
    
    armature.edit_bones['shoulder_driver.L'].parent = armature.edit_bones['ORG-spine.003']
    armature.edit_bones['shoulder_driver.R'].parent = armature.edit_bones['ORG-spine.003']
    armature.edit_bones['MCH-shoulder_follow.L'].parent = armature.edit_bones['ORG-spine.003']
    armature.edit_bones['MCH-shoulder_follow.R'].parent = armature.edit_bones['ORG-spine.003']
    armature.edit_bones['shoulder.L'].parent = armature.edit_bones['MCH-shoulder_follow.L']
    armature.edit_bones['shoulder.R'].parent = armature.edit_bones['MCH-shoulder_follow.R']
   
    # RENAME imported bones
    rename_bones_list = [("root", "root.002")]
    rename_bones_list.append(("root-inner", "root.001"))
    rename_bones_list.append(("root-outer", "root"))
    
    rename_bones_list.append(("torso", "torso.002"))
    rename_bones_list.append(("torso-inner", "torso.001"))
    rename_bones_list.append(("torso-outer", "torso"))
    
    rename_bones_list.append(("ik-pivot-L", "foot_ik_pivot.L"))
    rename_bones_list.append(("mch-ik-pivot-L", "MCH-foot_ik_pivot.L"))
    rename_bones_list.append(("ik-sub-pivot-L", "foot_ik_sub.L"))
    rename_bones_list.append(("ik-target-L", "MCH-thigh_ik_target_sub.L"))
    
    rename_bones_list.append(("ik-pivot-R", "foot_ik_pivot.R"))
    rename_bones_list.append(("mch-ik-pivot-R", "MCH-foot_ik_pivot.R"))
    rename_bones_list.append(("ik-sub-pivot-R", "foot_ik_sub.R"))
    rename_bones_list.append(("ik-target-R", "MCH-thigh_ik_target_sub.R"))
    
    rename_bones_list.append(("hand_ik.L", "hand_ik_wrist.L"))
    rename_bones_list.append(("hand-ik-L", "hand_ik.L"))
    rename_bones_list.append(("hand-ik-pivot-L", "hand_ik_pivot.L"))
    rename_bones_list.append(("mch-hand-ik-pivot-L", "MCH-hand_ik_pivot.L"))
    rename_bones_list.append(("mch-hand-ik-wrist-L", "MCH-hand_ik_wrist.L"))
    
    rename_bones_list.append(("hand_ik.R", "hand_ik_wrist.R"))
    rename_bones_list.append(("hand-ik-R", "hand_ik.R"))
    rename_bones_list.append(("hand-ik-pivot-R", "hand_ik_pivot.R"))
    rename_bones_list.append(("mch-hand-ik-pivot-R", "MCH-hand_ik_pivot.R"))
    rename_bones_list.append(("mch-hand-ik-wrist-R", "MCH-hand_ik_wrist.R"))

    
    # TORSO POS fixing
    # armature.edit_bones['torso'].roll = -1.5708
    torso_head_pos = armature.edit_bones['torso'].head.copy()
    torso_tail_pos = armature.edit_bones['torso'].tail.copy()
    
    armature.edit_bones['torso-inner'].head = torso_head_pos
    armature.edit_bones['torso-inner'].tail = torso_tail_pos
    armature.edit_bones['torso-inner'].tail.y += 0.05
    
    armature.edit_bones['torso-outer'].head = torso_head_pos
    armature.edit_bones['torso-outer'].tail = torso_tail_pos
    armature.edit_bones['torso-outer'].tail.y += 0.1
    
    armature.edit_bones['torso_pivot.002'].head = torso_head_pos
    armature.edit_bones['torso_pivot.002'].tail = torso_tail_pos
    
    armature.edit_bones['MCH-torso_pivot.002'].head = torso_head_pos
    armature.edit_bones['MCH-torso_pivot.002'].tail = torso_tail_pos
    armature.edit_bones['MCH-torso_pivot.002'].length -= 0.09
    
    # FOOT POS fixing: Remember to use old bone names pre renaming
    foot_L_z_diff = armature.edit_bones['foot_ik.L'].tail.z - armature.edit_bones['foot_spin_ik.L'].tail.z
    foot_R_z_diff = armature.edit_bones['foot_ik.R'].tail.z - armature.edit_bones['foot_spin_ik.R'].tail.z
       
    armature.edit_bones['ik-sub-pivot-L'].head = armature.edit_bones['foot_ik.L'].head.copy()
    armature.edit_bones['ik-sub-pivot-L'].tail = armature.edit_bones['foot_ik.L'].tail.copy()
    
    armature.edit_bones['ik-sub-pivot-R'].head = armature.edit_bones['foot_ik.R'].head.copy()
    armature.edit_bones['ik-sub-pivot-R'].tail = armature.edit_bones['foot_ik.R'].tail.copy()
    
    armature.edit_bones['ik-pivot-L'].head = armature.edit_bones['MCH-heel.02_roll2.L'].head.copy()
    armature.edit_bones['ik-pivot-L'].tail = armature.edit_bones['MCH-heel.02_roll2.L'].tail.copy()
    armature.edit_bones['ik-pivot-L'].tail.y += 0.05
    
    armature.edit_bones['ik-pivot-R'].head = armature.edit_bones['MCH-heel.02_roll2.R'].head.copy()
    armature.edit_bones['ik-pivot-R'].tail = armature.edit_bones['MCH-heel.02_roll2.R'].tail.copy()
    armature.edit_bones['ik-pivot-R'].tail.y += 0.05
    
    armature.edit_bones['mch-ik-pivot-L'].head = armature.edit_bones['MCH-heel.02_roll2.L'].head.copy()
    armature.edit_bones['mch-ik-pivot-L'].tail = armature.edit_bones['MCH-heel.02_roll2.L'].tail.copy()
    
    armature.edit_bones['mch-ik-pivot-R'].head = armature.edit_bones['MCH-heel.02_roll2.R'].head.copy()
    armature.edit_bones['mch-ik-pivot-R'].tail = armature.edit_bones['MCH-heel.02_roll2.R'].tail.copy()
    
    armature.edit_bones['ik-target-L'].head = armature.edit_bones['foot_tweak.L'].head.copy()
    armature.edit_bones['ik-target-L'].tail = armature.edit_bones['foot_tweak.L'].tail.copy()
    
    armature.edit_bones['ik-target-R'].head = armature.edit_bones['foot_tweak.R'].head.copy()
    armature.edit_bones['ik-target-R'].tail = armature.edit_bones['foot_tweak.R'].tail.copy()
    
    foot_L_x_diff = armature.edit_bones['ik-sub-pivot-L'].tail.x - armature.edit_bones['foot_spin_ik.L'].tail.x
    foot_R_x_diff = armature.edit_bones['ik-sub-pivot-R'].tail.x - armature.edit_bones['foot_spin_ik.R'].tail.x
    
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].head = armature.edit_bones['MCH-shin_ik.L'].head.copy()
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].tail.z = armature.edit_bones['MCH-shin_ik.L'].tail.z
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].tail.x = armature.edit_bones['MCH-shin_ik.L'].tail.x
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].roll = 0
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].length = .02
    
    armature.edit_bones['shin_tweak-pin.L'].head = armature.edit_bones['MCH-shin_ik.L'].head.copy()
    armature.edit_bones['shin_tweak-pin.L'].tail = armature.edit_bones['MCH-shin_ik.L'].tail.copy()
    armature.edit_bones['shin_tweak-pin.L'].roll = armature.edit_bones['MCH-shin_ik.L'].roll
    armature.edit_bones['shin_tweak-pin.L'].length -= 0.15
    
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].head = armature.edit_bones['MCH-shin_ik.R'].head.copy()
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].tail.z = armature.edit_bones['MCH-shin_ik.R'].tail.z
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].tail.x = armature.edit_bones['MCH-shin_ik.R'].tail.x
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].roll = 0
    armature.edit_bones['MCH-shin_tweak-pin.parent.R'].length = .02
    
    armature.edit_bones['shin_tweak-pin.R'].head = armature.edit_bones['MCH-shin_ik.R'].head.copy()
    armature.edit_bones['shin_tweak-pin.R'].tail = armature.edit_bones['MCH-shin_ik.R'].tail.copy()
    armature.edit_bones['shin_tweak-pin.R'].roll = armature.edit_bones['MCH-shin_ik.R'].roll
    armature.edit_bones['shin_tweak-pin.R'].length -= 0.15
    
    # HAND POS Fixing
    armature.edit_bones['hand-ik-L'].head = armature.edit_bones['hand_ik.L'].head.copy()
    armature.edit_bones['hand-ik-L'].tail = armature.edit_bones['hand_ik.L'].tail.copy()
    armature.edit_bones['hand-ik-L'].roll = armature.edit_bones['hand_ik.L'].roll
    
    armature.edit_bones['hand-ik-pivot-L'].head = armature.edit_bones['hand_ik.L'].head.copy()
    armature.edit_bones['hand-ik-pivot-L'].tail = armature.edit_bones['hand_ik.L'].tail.copy()
    armature.edit_bones['hand-ik-pivot-L'].roll = armature.edit_bones['hand_ik.L'].roll
    
    armature.edit_bones['mch-hand-ik-pivot-L'].head = armature.edit_bones['hand_ik.L'].head.copy()
    armature.edit_bones['mch-hand-ik-pivot-L'].tail = armature.edit_bones['hand_ik.L'].tail.copy()
    armature.edit_bones['mch-hand-ik-pivot-L'].roll = armature.edit_bones['hand_ik.L'].roll
    armature.edit_bones['mch-hand-ik-pivot-L'].length -= 0.03
    
    armature.edit_bones['mch-hand-ik-wrist-L'].head = armature.edit_bones['hand_ik.L'].head.copy()
    armature.edit_bones['mch-hand-ik-wrist-L'].tail = armature.edit_bones['hand_ik.L'].tail.copy()
    armature.edit_bones['mch-hand-ik-wrist-L'].roll = armature.edit_bones['hand_ik.L'].roll
    armature.edit_bones['mch-hand-ik-wrist-L'].length -= 0.04
    
    armature.edit_bones['hand-ik-R'].head = armature.edit_bones['hand_ik.R'].head.copy()
    armature.edit_bones['hand-ik-R'].tail = armature.edit_bones['hand_ik.R'].tail.copy()
    armature.edit_bones['hand-ik-R'].roll = armature.edit_bones['hand_ik.R'].roll
    
    armature.edit_bones['hand-ik-pivot-R'].head = armature.edit_bones['hand_ik.R'].head.copy()
    armature.edit_bones['hand-ik-pivot-R'].tail = armature.edit_bones['hand_ik.R'].tail.copy()
    armature.edit_bones['hand-ik-pivot-R'].roll = armature.edit_bones['hand_ik.R'].roll
    
    armature.edit_bones['mch-hand-ik-pivot-R'].head = armature.edit_bones['hand_ik.R'].head.copy()
    armature.edit_bones['mch-hand-ik-pivot-R'].tail = armature.edit_bones['hand_ik.R'].tail.copy()
    armature.edit_bones['mch-hand-ik-pivot-R'].roll = armature.edit_bones['hand_ik.R'].roll
    armature.edit_bones['mch-hand-ik-pivot-R'].length -= 0.03
    
    armature.edit_bones['mch-hand-ik-wrist-R'].head = armature.edit_bones['hand_ik.R'].head.copy()
    armature.edit_bones['mch-hand-ik-wrist-R'].tail = armature.edit_bones['hand_ik.R'].tail.copy()
    armature.edit_bones['mch-hand-ik-wrist-R'].roll = armature.edit_bones['hand_ik.R'].roll
    armature.edit_bones['mch-hand-ik-wrist-R'].length -= 0.04
    
    armature.edit_bones['MCH-forearm_tweak-pin.parent.L'].head = armature.edit_bones['MCH-forearm_ik.L'].head.copy()
    armature.edit_bones['MCH-forearm_tweak-pin.parent.L'].tail.z = armature.edit_bones['MCH-forearm_ik.L'].tail.z
    armature.edit_bones['MCH-forearm_tweak-pin.parent.L'].tail.x = armature.edit_bones['MCH-forearm_ik.L'].tail.x
    armature.edit_bones['MCH-forearm_tweak-pin.parent.L'].roll = 0
    armature.edit_bones['MCH-forearm_tweak-pin.parent.L'].length = .02
    
    armature.edit_bones['forearm_tweak-pin.L'].head = armature.edit_bones['MCH-forearm_ik.L'].head.copy()
    armature.edit_bones['forearm_tweak-pin.L'].tail = armature.edit_bones['MCH-forearm_ik.L'].tail.copy()
    armature.edit_bones['forearm_tweak-pin.L'].roll = armature.edit_bones['MCH-forearm_ik.L'].roll
    armature.edit_bones['forearm_tweak-pin.L'].length -= 0.15
    
    armature.edit_bones['MCH-forearm_tweak-pin.parent.R'].head = armature.edit_bones['MCH-forearm_ik.R'].head.copy()
    armature.edit_bones['MCH-forearm_tweak-pin.parent.R'].tail.z = armature.edit_bones['MCH-forearm_ik.R'].tail.z
    armature.edit_bones['MCH-forearm_tweak-pin.parent.R'].tail.x = armature.edit_bones['MCH-forearm_ik.R'].tail.x
    armature.edit_bones['MCH-forearm_tweak-pin.parent.R'].roll = 0
    armature.edit_bones['MCH-forearm_tweak-pin.parent.R'].length = .02
    
    armature.edit_bones['forearm_tweak-pin.R'].head = armature.edit_bones['MCH-forearm_ik.R'].head.copy()
    armature.edit_bones['forearm_tweak-pin.R'].tail = armature.edit_bones['MCH-forearm_ik.R'].tail.copy()
    armature.edit_bones['forearm_tweak-pin.R'].roll = armature.edit_bones['MCH-forearm_ik.R'].roll
    armature.edit_bones['forearm_tweak-pin.R'].length -= 0.15
    
    armature.edit_bones['shoulder_driver.L'].head = project_line_in_space(armature.edit_bones['shoulder.L'].head.copy(),armature.edit_bones['shoulder.L'].tail.copy(), armature.edit_bones['hand_ik.L'].head.x)
    armature.edit_bones['shoulder_driver.L'].tail = project_line_in_space(armature.edit_bones['shoulder.L'].head.copy(),armature.edit_bones['shoulder.L'].tail.copy(), armature.edit_bones['hand_ik.L'].head.x)
    armature.edit_bones['shoulder_driver.L'].tail.y += 0.1
    
    armature.edit_bones['shoulder_driver.R'].head = project_line_in_space(armature.edit_bones['shoulder.R'].head.copy(),armature.edit_bones['shoulder.R'].tail.copy(), armature.edit_bones['hand_ik.R'].head.x)
    armature.edit_bones['shoulder_driver.R'].tail = project_line_in_space(armature.edit_bones['shoulder.R'].head.copy(),armature.edit_bones['shoulder.R'].tail.copy(), armature.edit_bones['hand_ik.R'].head.x)
    armature.edit_bones['shoulder_driver.R'].tail.y += 0.1
    
    armature.edit_bones['MCH-shoulder_follow.L'].head = armature.edit_bones['shoulder.L'].head.copy()
    armature.edit_bones['MCH-shoulder_follow.L'].tail = armature.edit_bones['shoulder.L'].tail.copy()
    
    armature.edit_bones['MCH-shoulder_follow.R'].head = armature.edit_bones['shoulder.R'].head.copy()
    armature.edit_bones['MCH-shoulder_follow.R'].tail = armature.edit_bones['shoulder.R'].tail.copy()

   
    try:
        armature.edit_bones["DEF-eye.L"].name = "+EyeBone L A01"
        armature.edit_bones["DEF-eye.R"].name = "+EyeBone R A01"

        # Properly finish the parenting of the eye rig we imported!
        armature.edit_bones['eyetrack'].parent = armature.edit_bones['head']
        armature.edit_bones['+EyeBone R A01.001'].parent = armature.edit_bones['head']
        armature.edit_bones['+EyeBone L A01.001'].parent = armature.edit_bones['head']

        # Now we need to position them to the existing bones.
        eye_R_head_pos = armature.edit_bones['+EyeBone R A01'].head
        eye_L_head_pos = armature.edit_bones['+EyeBone L A01'].head


        armature.edit_bones['+EyeBone R A01.001'].head = eye_R_head_pos
        armature.edit_bones['+EyeBone R A01.001'].tail.x = eye_R_head_pos[0]
        armature.edit_bones['+EyeBone R A01.001'].tail.y = armature.edit_bones['+EyeBone R A01'].tail.y
        armature.edit_bones['+EyeBone R A01.001'].tail.z = eye_R_head_pos[2]

        armature.edit_bones['+EyeBone L A01.001'].head = eye_L_head_pos
        armature.edit_bones['+EyeBone L A01.001'].tail.x = eye_L_head_pos[0]
        armature.edit_bones['+EyeBone L A01.001'].tail.y = armature.edit_bones['+EyeBone L A01'].tail.y
        armature.edit_bones['+EyeBone L A01.001'].tail.z = eye_L_head_pos[2]

        armature.edit_bones['eyetrack_R'].head.x = eye_R_head_pos[0]
        armature.edit_bones['eyetrack_R'].head.z = eye_R_head_pos[2]

        armature.edit_bones['eyetrack_R'].tail.x = eye_R_head_pos[0]
        armature.edit_bones['eyetrack_R'].tail.z = eye_R_head_pos[2] + 0.01

        armature.edit_bones['eyetrack_L'].head.x = eye_L_head_pos[0]
        armature.edit_bones['eyetrack_L'].head.z = eye_L_head_pos[2]

        armature.edit_bones['eyetrack_L'].tail.x = eye_L_head_pos[0]
        armature.edit_bones['eyetrack_L'].tail.z = eye_L_head_pos[2] + 0.01

        armature.edit_bones['eyetrack'].head.x = (eye_R_head_pos[0]+eye_L_head_pos[0])/2
        armature.edit_bones['eyetrack'].head.z = (eye_R_head_pos[2]+eye_L_head_pos[2])/2

        armature.edit_bones['eyetrack'].tail.x = (eye_R_head_pos[0]+eye_L_head_pos[0])/2
        armature.edit_bones['eyetrack'].tail.z = armature.edit_bones['eyetrack_L'].tail.z
    except:
        pass


    # Still in edit mode, select Neck/Head bone and extract the Z loc 
    neck_bone = armature.edit_bones['neck']
    neck_pos = neck_bone.head[2]

    if(use_head_tracker):
        # Let's position our head controller bone here. We need it to match our head bone's position
        head_bone = armature.edit_bones['head']
        head_pos_head2 = head_bone.head[2]
        head_pos_tail2 = head_bone.tail[2]
        head_pos_head1 = head_bone.head[1]
        head_pos_tail1 = head_bone.tail[1]

        # Select the head controller bone and position w/ head bone's location.
        head_cont_bone =  armature.edit_bones['head-controller']
        head_cont_bone.head[0] = 0
        head_cont_bone.head[1] = -0.3
        head_cont_bone.head[2] = head_pos_head2
        head_cont_bone.tail[0] = 0
        head_cont_bone.tail[1] = -0.3
        head_cont_bone.tail[2] = head_pos_tail2

    # Delete ugly lines that connect to the pole bones.
    def del_bone(bone_name):
        to_del = armature.edit_bones.get(bone_name)
        armature.edit_bones.remove(to_del)
        
    del_bone("VIS_upper_arm_ik_pole.L")
    del_bone("VIS_upper_arm_ik_pole.R")
    del_bone("VIS_thigh_ik_pole.L")
    del_bone("VIS_thigh_ik_pole.R")
    
    del_bone("palm.L")
    del_bone("palm.R")

    # Function that validates bone name given for respective area. (if bone passes checks to be considered front)
    def validate_skirt(bone_name, area):
        # Below is the list of bone 'prefix's we consider valid to send into the skirt/dress lists
        if bone_name.startswith("+Skirt"):
            temp_name = bone_name[6:]
        elif bone_name.startswith("+Hem"):
            temp_name = bone_name[4:]
        elif bone_name.startswith("+Overcoat"):
            temp_name = bone_name[9:]
        elif bone_name.startswith("+VisionPelvis"):
            temp_name = bone_name[13:]
        else: return False
                  
        if area == "FRONT":
            if temp_name[0] == "F":
                return True
            
        elif area == "SIDE":
            if temp_name[0] == "S":
                return True
            
        elif area == "BACK":
            if temp_name[0] == "B":
                return True
            
        else: return False
    # Certain bones with skirt naming exist with pelvis spine as parent, but theyre NOT skirt bones we want. remove them.    
    def trunc_bad_bones(pb, current=None):
        bad = []
        if current is None:
            current = pb
        
        current_bone = armature.edit_bones[current]
        
        for bone in armature.edit_bones:
            if bone.parent == current_bone:
                bad.append(bone.name)
                bad.extend(trunc_bad_bones(pb, bone.name))
                
        return bad
    
    list_of_bad_bones = trunc_bad_bones("DEF-spine.003")

    # Functions that loop through skirt bones (Front, Sides, Back) each return a list
    def identify_children_for_skirt(pb, current=None, excluded_parent="DEF-spine.003"):
        child_bones = []
        if current is None:
            current = pb
        
        current_bone = armature.edit_bones[current]
        
        for bone in armature.edit_bones:
            if bone.parent == excluded_parent:
                continue
            elif bone.parent == current_bone:
                child_bones.append(bone)
                child_bones.extend(identify_children_for_skirt(pb, bone.name, excluded_parent))
                
        return child_bones
    
    parent_bone_name = "DEF-spine.001"
    weird_skeletons = ["Clorinde"]
    for s in weird_skeletons:
        if s in char_name:
            parent_bone_name = "+PelvisTwist CF A01"
            
    skirt_children = identify_children_for_skirt(parent_bone_name)
    
    def scan_skirt(area):
        skirt_bones = []
             
        for edit_bone in skirt_children:
            if edit_bone.name not in list_of_bad_bones:
                if validate_skirt(edit_bone.name, area):
                    skirt_bones.append(edit_bone.name)

        return skirt_bones

    # On each list, straighten the bone (Straighten on the head)
    front_skirt_bones = scan_skirt("FRONT")
    side_skirt_bones = scan_skirt("SIDE")
    back_skirt_bones = scan_skirt("BACK")

    def zero_roll(bone_name):
        this_bone = armature.edit_bones[bone_name].roll = 0
    for bone in front_skirt_bones:
        zero_roll(bone)
        
    for bone in side_skirt_bones:
        zero_roll(bone)
        
    for bone in back_skirt_bones:
        zero_roll(bone)                                                            
    # In pose mode select the rig, then select the bone
    bpy.ops.object.mode_set(mode='POSE')
    faceplate_arm =  bpy.context.scene.objects[char_name+"Rig"]
    selected_bone = faceplate_arm.pose.bones["Plate"]

    # Change the values to what we want, use neckpos to base the height off the ground.
    selected_bone.location[0] = .33
    #selected_bone.location[1] = 0.9
    selected_bone.location[2] = neck_pos
    selected_bone.rotation_quaternion[1] = 1
    selected_bone.scale[0] = 0.1
    selected_bone.scale[1] = 0.1
    selected_bone.scale[2] = 0.1



    # Begin moving extra wgt bones to the wgt collection while discarding old collections
    # 1 Root and Eye Bones
    move_into_collection("eye circle","wgt")
    move_into_collection("eye controller","wgt")
    move_into_collection("root plate","wgt")
    move_into_collection("head-control-shape","wgt")

    # 1 Face Bones
    to_del_coll = bpy.data.collections.get("wgt.001")
    for obj in to_del_coll.objects:
        move_into_collection(obj.name,"wgt")
    
    # 2 Pelvis Bones
    to_del_coll = bpy.data.collections.get("wgt.002")
    for obj in to_del_coll.objects:
        move_into_collection(obj.name,"wgt")
    
    # 3 feet Bones
    to_del_coll = bpy.data.collections.get("wgt.003")
    for obj in to_del_coll.objects:
        move_into_collection(obj.name,"wgt")
        
    # 4 hand Bones
    to_del_coll = bpy.data.collections.get("wgt.004")
    for obj in to_del_coll.objects:
        move_into_collection(obj.name,"wgt")
        
    # idk bro math is wrong delete whatever this is too
    to_del_coll = bpy.data.collections.get("wgt.005")
    for obj in to_del_coll.objects:
        move_into_collection(obj.name,"wgt")
        
    to_del_coll = bpy.data.collections.get("wgt.006")
    for obj in to_del_coll.objects:
        move_into_collection(obj.name,"wgt")

    # After moving into collection, delete the old empty ones.
    bpy.data.collections.remove(bpy.data.collections.get("append_Root"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Face Plate"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Eyes"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Pelvis"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Foot"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Hand"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Props"),do_unlink=True)

    # Adding Shape Key Drivers
    ourRig = char_name+"Rig"

    # Loop through skirt bones list. 

    # converts deg to calc
    def rad(num):
        return num * (pi/180) 

    # Perform more operations on number if needed.
    def calc(num, cut=False):
        percent = 0.8
        if cut:
            return rad(num*percent)
        else: return rad(num)

    # For front bones adjust number by depth
    def add_const(skirt_bone, name, bone, expression, driver=True, trans_rot="ROT_X", f_min_x=calc(-1), f_max_x = calc(1), f_min_y = 0, f_max_y = 0, f_min_z = 0, f_max_z = 0, map_x='X', map_y='Y', map_z='Z', t_min_x=0, t_max_x=0, t_min_y=0, t_max_y=0, t_min_z=0, t_max_z=0):
        armature = bpy.context.scene.objects[ourRig]

        this_bone = bpy.context.scene.objects[char_name+"Rig"].pose.bones[skirt_bone]
        co = this_bone.constraints.new('TRANSFORM')
        co.name = name
        co.target = our_char
        co.subtarget = bone
        co.use_motion_extrapolate = True

        if driver and name != "X":
            influence_driver = co.driver_add("influence").driver
            # DRIVER STUFF
            var = influence_driver.variables.new()
            var.name = "bone"
            var.type = 'TRANSFORMS'
            
            var.targets[0].id = armature
            var.targets[0].bone_target = bone
            var.targets[0].transform_space = 'LOCAL_SPACE'
            var.targets[0].transform_type = trans_rot
            
            var2 = influence_driver.variables.new()
            var2.name = "toggle"
            var2.type = "SINGLE_PROP"
            
            var2.targets[0].id = armature
            var2.targets[0].data_path = "pose.bones[\"plate-settings\"][\"Toggle Skirt Constraints\"]"

            influence_driver.type = 'SCRIPTED'
            influence_driver.expression = "(" + expression + ")*toggle" 

            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
            # END DRIVER STUFF
            
        # drivers for just the sides    
        elif driver and name == "X":
            influence_driver = co.driver_add("influence").driver
            # DRIVER STUFF
            var2 = influence_driver.variables.new()
            var2.name = "toggle"
            var2.type = "SINGLE_PROP"
            
            var2.targets[0].id = armature
            var2.targets[0].data_path = "pose.bones[\"plate-settings\"][\"Toggle Skirt Constraints\"]"

            influence_driver.type = 'SCRIPTED'
            influence_driver.expression = "toggle" 

            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
            
        co.target_space = "LOCAL"
        co.owner_space = "LOCAL"
        co.map_from = "ROTATION"
        co.map_to = "ROTATION"
        
        # Do transform constraint math
        # MAP FROM (put in t/e block?)
        co.from_min_x_rot = f_min_x
        co.from_max_x_rot = f_max_x
        
        co.from_min_y_rot = f_min_y
        co.from_max_y_rot = f_max_y
        
        co.from_min_z_rot = f_min_z
        co.from_max_z_rot = f_max_z
        
        # MAP TO
        co.map_to_x_from = map_x
        co.to_min_x_rot = t_min_x
        co.to_max_x_rot = t_max_x
        
        co.map_to_y_from = map_y
        co.to_min_y_rot = t_min_y
        co.to_max_y_rot = t_max_y
        
        co.map_to_z_from = map_z
        co.to_min_z_rot = t_min_z
        co.to_max_z_rot = t_max_z
        
       
    def add_leg_follow_const(bone_name, area):
    # skirt_bone, name, bone, f_min_x=calc(-1), f_max_x=calc(1), f_min_y=0, f_max_y=0, f_min_z=0, f_max_z=0, map_x='X', map_y='Y', map_z='Z', t_min_x=0, t_max_x=0, t_min_y=0, t_max_y=0, t_min_z=0, t_max_y=0

        # FRONT
        if area == "FRONT":
            # Front Center
            if " CF " in bone_name:
                if bone_name[-1] == "1":    
                    add_const(bone_name, "Left Leg", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="X", map_z="X", t_min_x=calc(-0.125), t_max_x=calc(0.125), t_min_y=calc(0.5), t_max_y=calc(-0.5), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Right Leg", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="X", map_z="Z", t_min_x=calc(-0.125), t_max_x=calc(0.125), t_min_y=calc(-0.5), t_max_y=calc(0.5), t_min_z=calc(0), t_max_z=calc(0))
                
                elif bone_name[-1] == "2": 
                    add_const(bone_name, "Left Leg", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="X", map_z="X", t_min_x=calc(0.125,True), t_max_x=calc(-0.125,True), t_min_y=calc(0.5,True), t_max_y=calc(-0.5,True), t_min_z=calc(-0.125,True), t_max_z=calc(0.125,True))
                    add_const(bone_name, "Right Leg", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="X", map_z="X", t_min_x=calc(0.125), t_max_x=calc(-0.125), t_min_y=calc(-0.5), t_max_y=calc(0.5), t_min_z=calc(0.125), t_max_z=calc(-0.125))
              
                elif bone_name[-1] == "3":                 
                    add_const(bone_name, "Left Leg", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="X", map_z="X", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0.5,True), t_max_y=calc(-0.5,True), t_min_z=calc(0.125,True), t_max_z=calc(-0.125,True))
                    add_const(bone_name, "Right Leg", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="X", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(-0.5,True), t_max_y=calc(0.5,True), t_min_z=calc(0), t_max_z=calc(0))
             # Front Left
            elif ".L" in bone_name:
                if bone_name[-3] == "1":
                    add_const(bone_name, "X+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.75,True), t_max_x=calc(0.75,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "X-", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3,True), t_max_x=calc(0.3,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", f_min_x=0, f_max_x=0, f_min_z=calc(-1), f_max_z=calc(1), map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.1,True), t_max_z=calc(0.1,True))

                elif bone_name[-3] == "2":
                    add_const(bone_name, "Transformation", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="X", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0.125,True), t_max_z=calc(0.0))
                elif bone_name[-3] == "3":   
                    add_const(bone_name, "Transformation", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
            elif " L " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "X+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.75,True), t_max_x=calc(0.75,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "X-", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3,True), t_max_x=calc(0.3,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", f_min_x=0, f_max_x=0, f_min_z=calc(-1), f_max_z=calc(1), map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.1,True), t_max_z=calc(0.1,True))

                elif bone_name[-1] == "2":
                    add_const(bone_name, "Transformation", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="X", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0.125,True), t_max_z=calc(0.0))
                elif bone_name[-1] == "3":   
                    add_const(bone_name, "Transformation", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))

            # Front Right
            elif ".R" in bone_name:
                if bone_name[-3] == "1":       
                    add_const(bone_name, "X+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.75,True), t_max_x=calc(0.75,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "X-", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3,True), t_max_x=calc(0.3,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z", f_min_x=0, f_max_x=0, f_min_z=calc(-1), f_max_z=calc(1), map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.1), t_max_z=calc(0.1,True))
                elif bone_name[-3] == "2":       
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="X", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.125,True), t_max_z=calc(0))
                elif bone_name[-3] == "3":    
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
            elif " R " in bone_name:
                if bone_name[-1] == "1":       
                    add_const(bone_name, "X+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.75,True), t_max_x=calc(0.75,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "X-", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3,True), t_max_x=calc(0.3,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z", f_min_x=0, f_max_x=0, f_min_z=calc(-1), f_max_z=calc(1), map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.1), t_max_z=calc(0.1,True))
                elif bone_name[-1] == "2":       
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="X", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.125,True), t_max_z=calc(0))
                elif bone_name[-1] == "3":    
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
        
         # SIDE
        elif area == "SIDE": 
            # Side Left
            if ".L" in bone_name:
                if bone_name[-3] == "1":
                    add_const(bone_name, "X", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z",f_min_x=0,f_max_x=0,f_min_z=calc(-1),f_max_z=calc(1),map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.2), t_max_z=calc(0.2))
            
            # Side Right
            elif ".R" in bone_name:
                if bone_name[-3] == "1":
                    add_const(bone_name, "X", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z",f_min_x=0,f_max_x=0,f_min_z=calc(-1),f_max_z=calc(1),map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.2), t_max_z=calc(0.2))
            elif " L " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "X", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z",f_min_x=0,f_max_x=0,f_min_z=calc(-1),f_max_z=calc(1),map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.2), t_max_z=calc(0.2))
            
            # Side Right
            elif " R " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "X", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z",f_min_x=0,f_max_x=0,f_min_z=calc(-1),f_max_z=calc(1),map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.2), t_max_z=calc(0.2))
        
        # BACK
        elif area == "BACK":
            # Back Left
            if ".L" in bone_name:
                if bone_name[-3] == "1":
                    add_const(bone_name, "Transformation", "DEF-thigh.L", "0.5 + 0.5 * max(0, min(1, (bone)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3), t_max_x=calc(0.3), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
            
            # Back Right
            if ".R" in bone_name:
                if bone_name[-3] == "1":
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.5 + 0.5 * max(0, min(1, (bone)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3), t_max_x=calc(0.3), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    # Back Left
            elif " L " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "Transformation", "DEF-thigh.L", "0.5 + 0.5 * max(0, min(1, (bone)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3), t_max_x=calc(0.3), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
            
            # Back Right
            elif " R " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.5 + 0.5 * max(0, min(1, (bone)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3), t_max_x=calc(0.3), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                        
            # Back Center
            if " CB " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "Left Leg", "DEF-thigh.L", "0.5 + 0.5 * max(0, min(1, (bone)*3))", map_x="X", map_y="X", map_z="X", t_min_x=calc(-0.125), t_max_x=calc(0.125), t_min_y=calc(0.5), t_max_y=calc(-0.5), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Right Leg", "DEF-thigh.R", "0.5 + 0.5 * max(0, min(1, (bone)*3))", map_x="X", map_y="X", map_z="Z", t_min_x=calc(-0.125), t_max_x=calc(0.125), t_min_y=calc(-0.5), t_max_y=calc(0.5), t_min_z=calc(0), t_max_z=calc(0))
        
        
    for bone in front_skirt_bones:
        add_leg_follow_const(bone, "FRONT")

    for bone in side_skirt_bones:
        add_leg_follow_const(bone, "SIDE")

    for bone in back_skirt_bones:
        add_leg_follow_const(bone, "BACK")

    # Let's go into object mode and select the three face parts to begin adding shape key drivers
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.object.select_all(action='DESELECT')


    def makeCon(shape_key,bone_name,expression,transform):
        # Get the bone object by name
        armature = bpy.context.scene.objects[ourRig]  
        bone = armature.pose.bones[bone_name]

        # Create a driver for the shape key
        shape_key = obj.data.shape_keys.key_blocks[shape_key]  
        driver = shape_key.driver_add("value").driver

        # Create variables for the driver
        var = driver.variables.new()
        var.name = "bone"
        var.type = 'TRANSFORMS'
        var.targets[0].id = armature
        var.targets[0].bone_target = bone_name
        var.targets[0].transform_space = 'LOCAL_SPACE'
        var.targets[0].transform_type = transform

        # Create the scripted expression driver
        driver.type = 'SCRIPTED'
        driver.expression = expression  

        # Update the dependencies
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()
        
    # BROW SHAPE KEYS 
    # Get the selected object with the shape key
    try:
        obj = bpy.data.objects.get("Brow") or (bpy.data.objects.get("Body") if meshes_joined else None)
        makeCon("Brow_Down_L","Brow-L-Control","bone * -4","LOC_Y")
        makeCon("Brow_Down_R","Brow-R-Control","bone * -4","LOC_Y")
        makeCon("Brow_Up_L","Brow-L-Control","bone * 4","LOC_Y")
        makeCon("Brow_Up_R","Brow-R-Control","bone * 4","LOC_Y")
        makeCon("Brow_Trouble_L", "Brow-Trouble-L-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Trouble_R", "Brow-Trouble-R-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Smily_R", "Brow-Smily-R-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Smily_L", "Brow-Smily-L-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Angry_L", "Brow-Angry-L-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Angry_R", "Brow-Angry-R-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Shy_L", "Brow-Shy-L-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Shy_R", "Brow-Shy-R-Control", "bone * 2", "LOC_X")   
        makeCon("Brow_Squeeze_R", "Brow-R-Control", "bone * 4", "LOC_X")   
        makeCon("Brow_Squeeze_L", "Brow-L-Control", "bone * -4", "LOC_X")   
    except: 
        pass

    try:
        # EYE SHAPE KEYS
        obj = bpy.data.objects.get("Face_Eye") or (bpy.data.objects.get("Body") if meshes_joined else None)
        makeCon("Eye_WinkA_L","WinkA-L-Invis","bone * -.82","LOC_Y")
        makeCon("Eye_WinkA_R","WinkA-R-Invis","bone * -.82","LOC_Y")
        makeCon("Eye_WinkB_L","WinkB-L-Invis","bone * -.82","LOC_Y")
        makeCon("Eye_WinkB_R","WinkB-R-Invis","bone * -.82","LOC_Y")
        makeCon("Eye_WinkC_L","WinkC-L-Invis","bone * -.82","LOC_Y")
        makeCon("Eye_WinkC_R","WinkC-R-Invis","bone * -.82","LOC_Y")

        makeCon("Eye_Ha","Eye-Ha-Control","bone * -2.22","LOC_Y")
        makeCon("Eye_Jito","Eye-Jito-Control","bone * -2.22","LOC_Y")
        makeCon("Eye_Wail","Eye-Wail-Control","bone * -2.22","LOC_Y")
        makeCon("Eye_Hostility","Eye-Hostility-Control","bone * -2.22","LOC_Y")
        makeCon("Eye_Tired","Eye-Tired-Control","bone * -2.22","LOC_Y")
        makeCon("Eye_WUp","Eye-Up-Control","bone * -2.22","LOC_Y")
        makeCon("Eye_WDown","Eye-Down-Control","bone * -2.22","LOC_Y")
        makeCon("Eye_Lowereyelid","Eye-LowerEyelid-Control","bone * -2.22","LOC_Y")

        # Pupils shape key drivers are set up below
        obj = bpy.data.objects.get("EyeStar") or (bpy.data.objects.get("Body") if meshes_joined else None)
        makeCon("EyeStar","Eye-Star-Control","1+(bone*2.23)","LOC_Y")
        
    except: 
        pass

    # MOUTH SHAPE KEYS
    obj = bpy.data.objects.get("Face") or (bpy.data.objects.get("Body") if meshes_joined else None)
    makeCon("Mouth_Default","Mouth-Default-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_A01","Mouth-Control","bone * -1.33","LOC_Y")
    makeCon("Mouth_Open01","Mouth-Control","bone * 1.33","LOC_Y")
    makeCon("Mouth_Smile01","Mouth-Smile1-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Smile02","Mouth-Smile2-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Angry01","Mouth-Angry1-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Angry02","Mouth-Angry2-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Angry03","Mouth-Angry3-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Fury01","Mouth-Fury1-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Doya01","Mouth-Doya1-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Doya02","Mouth-Doya2-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Pero01","Mouth-Pero1-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Pero02","Mouth-Pero2-Control","bone * 1.67","LOC_X")
    makeCon("Mouth_Line01","Mouth-Control","bone * 1.33","LOC_X")
    makeCon("Mouth_Line02","Mouth-Control","bone * -1.33","LOC_X")
    makeCon("Mouth_Neko01","Mouth-Neko1-Control","bone * 1.67","LOC_X")

    # Special drivers for pushing pupils back on blink
    def makeCon2(shape_key,bn1,bn2,bn3,expression,transform):
        # Get the bone object by name
        armature = bpy.context.scene.objects[ourRig]  
        bone = armature.pose.bones[bn1]

        # Create a driver for the shape key
        shape_key = obj.data.shape_keys.key_blocks[shape_key]  
        driver = shape_key.driver_add("value").driver

        # Create variables for the driver
        var = driver.variables.new()
        var.name = "invisA"
        var.type = 'TRANSFORMS'
        var.targets[0].id = armature
        var.targets[0].bone_target = bn1
        var.targets[0].transform_space = 'LOCAL_SPACE'
        var.targets[0].transform_type = transform
        
        # Create variables for the driver
        var1 = driver.variables.new()
        var1.name = "invisB"
        var1.type = 'TRANSFORMS'
        var1.targets[0].id = armature
        var1.targets[0].bone_target = bn2
        var1.targets[0].transform_space = 'LOCAL_SPACE'
        var1.targets[0].transform_type = transform
        
        # Create variables for the driver
        var2 = driver.variables.new()
        var2.name = "invisC"
        var2.type = 'TRANSFORMS'
        var2.targets[0].id = armature
        var2.targets[0].bone_target = bn3
        var2.targets[0].transform_space = 'LOCAL_SPACE'
        var2.targets[0].transform_type = transform

        # Create the scripted expression driver
        driver.type = 'SCRIPTED'
        driver.expression = expression  

        # Update the dependencies
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()
    obj = bpy.data.objects.get("Body")
    try:
        makeCon2("pupil-pushback-R","WinkA-R-Invis","WinkB-R-Invis","WinkC-R-Invis","max(invisA * -1.55, invisB * -1.55, invisC * -1.55)","LOC_Y") # -1.45
        makeCon2("pupil-pushback-L","WinkA-L-Invis","WinkB-L-Invis","WinkC-L-Invis","max(invisA * -1.55, invisB * -1.55, invisC * -1.55)","LOC_Y")
    except:
        pass
    # Pupils shape key driver is set up below. Like Eye Star, the shape key has to be made FIRST before adding a driver

    if(use_head_tracker):
        # Since we're still in object mode, here we can add the head pole object in the neck to track head movement
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.data.objects["Empty"].name = "Head_Pole"
        bpy.data.objects["Head_Pole"].empty_display_size = 0.01
        bpy.data.objects["Head_Pole"].parent = bpy.data.objects[char_name+"Rig"]
        bpy.data.objects["Head_Pole"].parent_type = "BONE"
        bpy.data.objects["Head_Pole"].parent_bone = "neck"

    # Let's go into object mode and select the body for the pupil shape keys, and to control our glow sliders.
    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects.get("Body")  
    bpy.ops.object.select_all(action='DESELECT')

    try:
        makeCon("pupils","Eye-Pupil-Control","bone * -2.4","LOC_Y")
    except:
        pass

    # Going into pose mode with our character selected.
    bpy.ops.object.select_all(action='DESELECT')
    our_char =  bpy.data.objects.get(char_name+"Rig")
    if our_char:
        our_char.select_set(True)
        bpy.context.view_layer.objects.active = our_char
        
        bpy.ops.object.mode_set(mode='POSE')
        
        
    def add_driver_to_eyelid():
        eyelid_invis_bone = bpy.context.scene.objects[char_name+"Rig"].pose.bones["eyelid-invis-control"]
        eyelid_control_driver = eyelid_invis_bone.driver_add('location', 1).driver
        # Create variables for the driver
        var = eyelid_control_driver.variables.new()
        var.name = "bone"
        var.type = 'TRANSFORMS'
        var.targets[0].id = bpy.data.objects.get(ourRig)
        var.targets[0].bone_target = "eyetrack"
        var.targets[0].transform_space = 'LOCAL_SPACE'
        var.targets[0].transform_type = "LOC_Y"

        # Create the scripted expression driver
        eyelid_control_driver.type = 'SCRIPTED'
        eyelid_control_driver.expression = "bone * 5"  

        # Update the dependencies
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()

    try:
        add_driver_to_eyelid()
    except: 
        pass

    # Disable IK Stretching & Turn on IK Poles. Toggle manually as needed.
    if disallow_leg_ik_stretch:
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.L"]["IK_Stretch"] = 0.0
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.R"]["IK_Stretch"] = 0.0

    if disallow_arm_ik_stretch:
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.L"]["IK_Stretch"] = 0.0
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.R"]["IK_Stretch"] = 0.0
        
    if use_arm_ik_poles:
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.L"]["pole_vector"] = 1
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.R"]["pole_vector"] = 1
        
    if use_leg_ik_poles:
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.L"]["pole_vector"] = 1
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.R"]["pole_vector"] = 1

    bpy.data.objects[char_name+"Rig"].pose.bones["torso"]["head_follow"] = 1.0
    bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.L"]["IK_parent"] = 4
    bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.R"]["IK_parent"] = 4

    def add_shoulder_const(follow, driver, hand):
        armature = bpy.context.scene.objects[ourRig]
        
        # make shoulder follow driver bone
        this_bone = bpy.context.scene.objects[char_name+"Rig"].pose.bones[follow]
        co = this_bone.constraints.new('DAMPED_TRACK')
        co.target = our_char
        co.subtarget = driver
        
        # make driver bone follow hand
        drive = bpy.context.scene.objects[char_name+"Rig"].pose.bones[driver]
        co2 = drive.constraints.new('COPY_LOCATION')
        co2.target = our_char
        co2.subtarget = hand
        co2.target_space = "LOCAL_OWNER_ORIENT"
        co2.owner_space = "LOCAL"
        
        # make driver to control influence
        driver = co.driver_add("influence").driver
        var = driver.variables.new()
        var.name = "bone"
        var.type = 'SINGLE_PROP'
        
        var.targets[0].id = armature
        var.targets[0].data_path = "pose.bones[\"plate-settings\"][\"Toggle Shoulder Constraints\"]"
        driver.type = 'SCRIPTED'
        driver.expression = "(bone * 0.4)"
        
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()

    
    add_shoulder_const("MCH-shoulder_follow.L","shoulder_driver.L","hand-ik-L")
    add_shoulder_const("MCH-shoulder_follow.R","shoulder_driver.R","hand-ik-R")
    
    def add_eye_bone_const(bone_name, to_bone):
        this_bone = bpy.context.scene.objects[char_name+"Rig"].pose.bones[bone_name]
        co = this_bone.constraints.new('COPY_ROTATION')
        co.target = our_char
        co.subtarget = to_bone
        co.target_space = "LOCAL_OWNER_ORIENT"
        co.owner_space = "LOCAL"

    try:
        add_eye_bone_const("+EyeBone R A01", "+EyeBone R A01.001")
        add_eye_bone_const("+EyeBone L A01", "+EyeBone L A01.001")
    except:
        pass

    # Let's add empty 'child of' constraints to limbs, torso and root. Ready to use in case char holds obj/stands on obj
    def add_child_of(bone_name):
        this_bone = bpy.context.scene.objects[char_name+"Rig"].pose.bones[bone_name]
        co = this_bone.constraints.new('CHILD_OF')

    if add_child_of_constraints: 
        add_child_of("hand-ik-L")
        add_child_of("hand-ik-R")
        add_child_of("foot_ik.R")
        add_child_of("foot_ik.L")
        add_child_of("torso-outer")
        add_child_of("root")
        
        
    if(use_head_tracker):    

        # Here we can set up the two damped track constraints to make the head follow the controller bone.
        # This makes the head bone follow the controller
        head_controller = bpy.context.scene.objects[char_name+"Rig"].pose.bones["head"]
        co = head_controller.constraints.new('DAMPED_TRACK')
        head_track_const = bpy.data.objects[char_name+"Rig"].pose.bones["head"].constraints["Damped Track"]
        head_track_const.target = our_char 
        head_track_const.subtarget = "head-controller"
        head_track_const.track_axis = "TRACK_Z"

        # This makes the controller follow the obj in the neck to keep it 'on' the head.
        head_pole_cont = bpy.context.scene.objects[char_name+"Rig"].pose.bones["head-controller"]
        co2 = head_pole_cont.constraints.new('DAMPED_TRACK')
        head_pole_const = bpy.data.objects[char_name+"Rig"].pose.bones["head-controller"].constraints["Damped Track"]
        head_pole_const.target = bpy.data.objects.get("Head_Pole") 
        head_pole_const.track_axis = "TRACK_NEGATIVE_Z"

    # We can now make our final bone groups look good! (Both 3.6 and 4.0 functionality.)
    def assign_bone_to_group(bone_name, group_name):
        # Perform old functionality to make BGs to then color.
        if not is_version_4:
            # Switch to object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Get the armature object
            armature_obj = our_char
            if not armature_obj or armature_obj.type != 'ARMATURE':
                return

            # Switch to pose mode
            bpy.context.view_layer.objects.active = armature_obj
            bpy.ops.object.mode_set(mode='POSE')

            # Get the pose bone
            pose_bone = armature_obj.pose.bones.get(bone_name)
            if not pose_bone:
                return

            # Get the bone group
            bone_group = armature_obj.pose.bone_groups.get(group_name)
            if not bone_group:
                # Create a new bone group if it doesn't exist
                bone_group = armature_obj.pose.bone_groups.new(name=group_name)

            # Assign the bone to the bone group
            pose_bone.bone_group = bone_group
        
        # New 4.0 functionality: change the bone itself to the color of the group it was originally assigned to.
        else:
            # 4.0: Armature bones or Pose bones?
            bone = bpy.context.object.pose.bones[bone_name]
            
            if group_name == "Root":
                bone.color.palette = 'CUSTOM'
                bone.color.custom.normal = (0,1,0.169)
                bone.color.custom.select = (0.184,1,0.713)
                bone.color.custom.active = (0.125,0.949,0.816)
            elif group_name == "Torso":
                bone.color.palette = 'CUSTOM'
                bone.color.custom.normal = (1,0.867,0)
                bone.color.custom.select = (1,0.671,0.502)
                bone.color.custom.active = (0.949,0.431,0)
            elif group_name == "Limbs L":
                bone.color.palette = 'CUSTOM'
                bone.color.custom.normal = (1,0,1)
                bone.color.custom.select = (1,0.129,0.467)
                bone.color.custom.active = (1,0.518,0.969)
            elif group_name == "Limbs R":
                bone.color.palette = 'CUSTOM'
                bone.color.custom.normal = (0,0.839,1)
                bone.color.custom.select = (0.227,0.357,0.902)
                bone.color.custom.active = (0.035,0.333,0.878)
            elif group_name == "Face":
                bone.color.palette = 'CUSTOM'
                bone.color.custom.normal = (1,0,0)
                bone.color.custom.select = (0.506,0.902,0.078)
                bone.color.custom.active = (0.094,0.714,0.878)        

    # Root BG
    assign_bone_to_group("root", "Root")
    assign_bone_to_group("root-outer", "Root")
    assign_bone_to_group("root-inner", "Root")
    
    # Torso BG
    assign_bone_to_group("torso", "Torso")
    assign_bone_to_group("torso-inner", "Torso")
    assign_bone_to_group("torso-outer", "Torso")
    assign_bone_to_group("torso_pivot.002", "Torso")
    assign_bone_to_group("hips", "Torso")
    assign_bone_to_group("chest", "Torso")
    assign_bone_to_group("neck", "Torso")
    assign_bone_to_group("head-controller", "Torso")
    assign_bone_to_group("head", "Torso")

    # Left Arm BG
    assign_bone_to_group("hand_ik.L", "Limbs L")
    assign_bone_to_group("upper_arm_ik_target.L", "Limbs L")
    assign_bone_to_group("shoulder.L", "Limbs L")
    assign_bone_to_group("hand-ik-pivot-L", "Limbs L")
    assign_bone_to_group("hand-ik-L", "Limbs L")
    assign_bone_to_group("upper_arm_parent.L", "Limbs L")
    assign_bone_to_group("forearm_tweak-pin.L", "Limbs L")
    assign_bone_to_group("prop.L", "Limbs L")
    if not use_arm_ik_poles:
        assign_bone_to_group("upper_arm_ik.L", "Limbs L")

    # Right Arm BG
    assign_bone_to_group("hand_ik.R", "Limbs R")
    assign_bone_to_group("upper_arm_ik_target.R", "Limbs R")
    assign_bone_to_group("shoulder.R", "Limbs R")
    assign_bone_to_group("hand-ik-pivot-R", "Limbs R")
    assign_bone_to_group("hand-ik-R", "Limbs R")
    assign_bone_to_group("upper_arm_parent.R", "Limbs R")
    assign_bone_to_group("forearm_tweak-pin.R", "Limbs R")
    assign_bone_to_group("prop.R", "Limbs R")
    if not use_arm_ik_poles:
        assign_bone_to_group("upper_arm_ik.R", "Limbs R")

    # Left Foot BG
    assign_bone_to_group("foot_ik.L", "Limbs L")
    assign_bone_to_group("toe_ik.L", "Limbs L")
    assign_bone_to_group("foot_spin_ik.L", "Limbs L")
    assign_bone_to_group("foot_heel_ik.L", "Limbs L")
    assign_bone_to_group("thigh_ik_target.L", "Limbs L")
    assign_bone_to_group("ik-pivot-L", "Limbs L")
    assign_bone_to_group("ik-sub-pivot-L", "Limbs L")
    assign_bone_to_group("thigh_parent.L", "Limbs L")
    assign_bone_to_group("shin_tweak-pin.L", "Limbs L")
    if not use_leg_ik_poles:
        assign_bone_to_group("thigh_ik.L", "Limbs L")

    # Right Foot BG
    assign_bone_to_group("foot_ik.R", "Limbs R")
    assign_bone_to_group("toe_ik.R", "Limbs R")
    assign_bone_to_group("foot_spin_ik.R", "Limbs R")
    assign_bone_to_group("foot_heel_ik.R", "Limbs R")
    assign_bone_to_group("thigh_ik_target.R", "Limbs R")
    assign_bone_to_group("ik-pivot-R", "Limbs R")
    assign_bone_to_group("ik-sub-pivot-R", "Limbs R")
    assign_bone_to_group("thigh_parent.R", "Limbs R")
    assign_bone_to_group("shin_tweak-pin.R", "Limbs R")
    if not use_leg_ik_poles:
        assign_bone_to_group("thigh_ik.R", "Limbs R")

    # Face BG
    assign_bone_to_group("Mouth-Control", "Face")
    assign_bone_to_group("Mouth-Smile1-Control", "Face")
    assign_bone_to_group("Mouth-Smile2-Control", "Face")
    assign_bone_to_group("Mouth-Angry1-Control", "Face")
    assign_bone_to_group("Mouth-Angry2-Control", "Face")
    assign_bone_to_group("Mouth-Angry3-Control", "Face")
    assign_bone_to_group("Mouth-Fury1-Control", "Face")
    assign_bone_to_group("Mouth-Doya1-Control", "Face")
    assign_bone_to_group("Mouth-Doya2-Control", "Face")
    assign_bone_to_group("Mouth-Pero1-Control", "Face")
    assign_bone_to_group("Mouth-Pero2-Control", "Face")
    assign_bone_to_group("Mouth-Neko1-Control", "Face")
    assign_bone_to_group("Mouth-Default-Control", "Face")
    assign_bone_to_group("plate-settings", "Face")

    assign_bone_to_group("Eye-Down-Control", "Face")
    assign_bone_to_group("Eye-Up-Control", "Face")
    assign_bone_to_group("Eye-Jito-Control", "Face")
    assign_bone_to_group("Eye-Tired-Control", "Face")
    assign_bone_to_group("Eye-Hostility-Control", "Face")
    assign_bone_to_group("Eye-Wail-Control", "Face")
    assign_bone_to_group("Eye-LowerEyelid-Control", "Face")
    assign_bone_to_group("Eye-Ha-Control", "Face")
    assign_bone_to_group("Eye-WinkA-Control", "Face")
    assign_bone_to_group("Eye-WinkB-Control", "Face")
    assign_bone_to_group("Eye-WinkC-Control", "Face")
    assign_bone_to_group("Eye-Star-Control", "Face")
    assign_bone_to_group("Eye-Pupil-Control", "Face")
    assign_bone_to_group("eyetrack", "Face")
    assign_bone_to_group("eyetrack_L", "Face")
    assign_bone_to_group("eyetrack_R", "Face")

    assign_bone_to_group("Wink-Control-R", "Face")
    assign_bone_to_group("Wink-Control-L", "Face")
    assign_bone_to_group("Brow-Trouble-L-Control", "Face")
    assign_bone_to_group("Brow-Trouble-R-Control", "Face")
    assign_bone_to_group("Brow-Shy-R-Control", "Face")
    assign_bone_to_group("Brow-Shy-L-Control", "Face")
    assign_bone_to_group("Brow-Angry-R-Control", "Face")
    assign_bone_to_group("Brow-Angry-L-Control", "Face")
    assign_bone_to_group("Brow-Smily-R-Control", "Face")
    assign_bone_to_group("Brow-Smily-L-Control", "Face")
    assign_bone_to_group("Brow-R-Control", "Face")
    assign_bone_to_group("Brow-L-Control", "Face")
    
    try:
        this_obj.pose.bones["eyetrack_L"].custom_shape_scale_xyz = (2,2,2)
        this_obj.pose.bones["eyetrack_R"].custom_shape_scale_xyz = (2,2,2)
        this_obj.pose.bones["eyetrack"].custom_shape_scale_xyz = (6.5,5,1)
    except:
        pass

    # Default bone group colors are ugly. We can change them.
    def change_bone_group_colors(bone_group_name, color1, color2, color3):
        active_bg = bpy.context.active_object.pose.bone_groups[bone_group_name]
        active_bg.color_set = "CUSTOM"
        active_bg.colors.normal = Color((color1))
        active_bg.colors.select = Color((color2))
        active_bg.colors.active = Color((color3))
    
    if not is_version_4:    
        change_bone_group_colors('Root',(0,1,0.169),(0.184,1,0.713),(0.125,0.949,0.816))
        change_bone_group_colors('Torso',(1,0.867,0),(1,0.671,0.502),(0.949,0.431,0))
        change_bone_group_colors('Limbs L',(1,0,1),(1,0.129,0.467),(1,0.518,0.969))
        change_bone_group_colors('Limbs R',(0,0.839,1),(0.227,0.357,0.902),(0.035,0.333,0.878))
        change_bone_group_colors('Face',(1,0,0),(0.506,0.902,0.078),(0.094,0.714,0.878))


    # Automatically builds the constraint stuff for SWITCH PARENT. DO NOT FORGET TO REENABLE THE CONSTRAINTS BELOW!!!!!!
    def generate_switch_parent_constraints(toggle_parent, location_of_switcher):
        const = this_obj.pose.bones[toggle_parent].constraints["SWITCH PARENT"]
        const.targets[0].target = bpy.data.objects[char_name+"Rig"]
        const.targets[0].subtarget = "root"

        const.targets[1].target = bpy.data.objects[char_name+"Rig"]
        const.targets[1].subtarget = "root.001"

        const.targets[2].target = bpy.data.objects[char_name+"Rig"]
        const.targets[2].subtarget = "root.002"

        const.targets[3].target = bpy.data.objects[char_name+"Rig"]
        const.targets[3].subtarget = "torso.002"

        const.targets[4].target = bpy.data.objects[char_name+"Rig"]
        const.targets[4].subtarget = "chest"
        
        location_str = "pose.bones[\"" + location_of_switcher + "\"][\"parent_switch\"]"
        
        for x in range(5):
            driver = const.targets[x].driver_add("weight").driver
            var = driver.variables.new()
            var.name = "toggle"
            var.type = 'SINGLE_PROP'
            var.targets[0].id = bpy.context.scene.objects[ourRig]
            var.targets[0].data_path = location_str

            driver.type = 'SCRIPTED'
            driver.expression = "toggle == " + str(x+1) 

            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
        
        # Toggle the constraint off, we HAVE to reenable it later to work!!
        const.enabled = False
    
    
    # REENABLE CONSTRAINTS BELOW

    if use_head_tracker:
        generate_switch_parent_constraints("MCH-head-controller-parent","head-controller")
    
    # REENABLE THE CONSTRAINT BELOW.
    generate_switch_parent_constraints("MCH-forearm_tweak-pin.parent.L","forearm_tweak-pin.L")
    generate_switch_parent_constraints("MCH-forearm_tweak-pin.parent.R","forearm_tweak-pin.R")
    generate_switch_parent_constraints("MCH-shin_tweak-pin.parent.L","shin_tweak-pin.L")
    generate_switch_parent_constraints("MCH-shin_tweak-pin.parent.R","shin_tweak-pin.R")
            
    # For each tweak bone, we make the custom property, the constraint and driver.
    def prepare_tweak_bone(tweak_bone, pin_bone):
        # Make Custom Property
        cust_bone = this_obj.pose.bones[tweak_bone]
        cust_bone["tweak_pin"] = 0.00
        # Setting the min/max ranges: https://blender.stackexchange.com/a/258099
        id_prop = cust_bone.id_properties_ui("tweak_pin")
        id_prop.update(min=0.0,max=1.0)        

        # Make Constraint
        con = this_obj.pose.bones[tweak_bone].constraints.new('COPY_LOCATION')
        con.target = our_char
        con.subtarget = pin_bone
        
        path_str = "pose.bones[\"" + tweak_bone+"\"][\"tweak_pin\"]"
        
        driver = con.driver_add("influence").driver
        driver.type = 'SUM'
        var = driver.variables.new()
        var.name = "bone"
        var.type = 'SINGLE_PROP'
        var.targets[0].id = bpy.context.scene.objects[ourRig]
        var.targets[0].data_path = path_str
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()
    
    prepare_tweak_bone("forearm_tweak.L", "forearm_tweak-pin.L")
    prepare_tweak_bone("forearm_tweak.R", "forearm_tweak-pin.R")
    prepare_tweak_bone("shin_tweak.L", "shin_tweak-pin.L")
    prepare_tweak_bone("shin_tweak.R", "shin_tweak-pin.R")
    
    # To repair the now missing custom property, let's remake it.
    def make_torso_custom():
        cust_bone = this_obj.pose.bones["torso-outer"]
        cust_bone["torso_parent"] = 1
        id_prop = cust_bone.id_properties_ui("torso_parent")
        id_prop.update(min=0,max=2)  
    
    make_torso_custom()
        
    # Adjustments to positioning
    this_obj.pose.bones["foot_ik.L"].custom_shape_transform = bpy.data.objects[char_name+"Rig"].pose.bones["mch-ik-pivot-L"]
    this_obj.pose.bones["foot_ik.R"].custom_shape_transform = bpy.data.objects[char_name+"Rig"].pose.bones["mch-ik-pivot-R"]
    this_obj.pose.bones["hand-ik-L"].custom_shape_transform = bpy.data.objects[char_name+"Rig"].pose.bones["mch-hand-ik-pivot-L"]
    this_obj.pose.bones["hand-ik-R"].custom_shape_transform = bpy.data.objects[char_name+"Rig"].pose.bones["mch-hand-ik-pivot-R"]
    
    this_obj.pose.bones["ik-sub-pivot-L"].custom_shape_translation = (foot_L_x_diff*-1.0, 0.0, foot_L_z_diff*-1.0)
    this_obj.pose.bones["ik-sub-pivot-R"].custom_shape_translation = (foot_R_x_diff*-1.0, 0.0, foot_R_z_diff*-1.0)
        
        
    # Penultimate: Rename bones as needed
    for oldname, newname in rename_bones_list:
        bone = bpy.context.object.pose.bones.get(oldname)
        if bone is None:
            continue
        bone.name = newname
        
        # We have to nuke the existing driver in the torso. 
    def nuke_old_torso_const():       
        const = this_obj.pose.bones["MCH-torso.parent"].constraints
        to_del = [c for c in const]
        for c in to_del:
            const.remove(c)
            
        new = const.new('ARMATURE')
        new.name = 'SWITCH_PARENT'
        # add target
        new.targets.new()
        new.targets[0].target = bpy.data.objects[char_name+"Rig"]
        new.targets[0].subtarget = "root.002"
        
        location_str = "pose.bones[\"torso\"][\"torso_parent\"]"

        driver = new.targets[0].driver_add("weight").driver
        for variable in driver.variables:
            if variable.type == 'SINGLE_PROP':
                variable.targets[0].data_path = location_str

        driver.expression = "var == 1"

        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()
        
        # Toggle the constraint off, we HAVE to reenable it later to work!!
        new.enabled = False
   
    nuke_old_torso_const()
    
    # Use this to swap a variable in a constraint
    def swap_const_follow_in_const(bone, constraint_type, new_var):
        const = this_obj.pose.bones[bone].constraints     
        for c in const:
            if c.type == constraint_type:
                const.remove(c)   
        
        new = const.new(constraint_type)
        new.target = bpy.data.objects[char_name+"Rig"]
        new.subtarget = "torso.002"       
        
        driver = new.driver_add("influence").driver
        driver.type = 'SUM'
        for variable in driver.variables:
            if variable.type == 'SINGLE_PROP':
                variable.targets[0].data_path = new_var

        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()
    
    swap_const_follow_in_const("MCH-ROT-head","COPY_ROTATION","pose.bones[\"plate-settings\"][\"Head Follow\"]")
    swap_const_follow_in_const("MCH-ROT-neck","COPY_ROTATION","pose.bones[\"plate-settings\"][\"Neck Follow\"]")
        
    # Delete all existing bone collections, and make new ones.   
    if is_version_4:
        armature = bpy.context.object.data
        collections = armature.collections
        for coll in collections:
            collections.remove(coll)
        
        collections.new("Tweaks")
        collections.new("Pivots & Pins")
        collections.new("Offsets")
        collections.new("Props")
        collections.new("Face")
        collections.new("Torso (IK)")
        collections.new("Torso (FK)")
        collections.new("Fingers")
        collections.new("Fingers (Detail)")
        collections.new("Arm.L (IK)")
        collections.new("Arm.R (IK)")
        collections.new("Arm.L (FK)")
        collections.new("Arm.R (FK)")
        collections.new("Leg.L (IK)")
        collections.new("Leg.R (IK)")
        collections.new("Leg.L (FK)")
        collections.new("Leg.R (FK)")
        collections.new("Root")
        collections.new("Physics")
        collections.new("Cage")
        if lighting_panel_rig_obj:
            collections.new("Lighting")
        collections.new("Other")
        
        for bone in armature.bones:
            collections["Other"].assign(bone)
          
    #Thanks Enthralpy for the code to ensure that the arm/leg "gears" are moveable.
    for bone in ['thigh_parent.L', 'thigh_parent.R', 'upper_arm_parent.L', 'upper_arm_parent.R']:
        this_obj.pose.bones[bone].custom_shape_transform = None
        this_obj.pose.bones[bone].lock_location[0] = False
        this_obj.pose.bones[bone].lock_location[1] = False
        this_obj.pose.bones[bone].lock_location[2] = False
        this_obj.pose.bones[bone].lock_rotation_w = False
        this_obj.pose.bones[bone].lock_rotation[0] = False
        this_obj.pose.bones[bone].lock_rotation[1] = False
        this_obj.pose.bones[bone].lock_rotation[2] = False
        this_obj.pose.bones[bone].lock_scale[0] = False
        this_obj.pose.bones[bone].lock_scale[1] = False
        this_obj.pose.bones[bone].lock_scale[2] = False
               
        # Customize bones
        this_obj.pose.bones[bone].custom_shape = bpy.data.objects["setting-circle"]
        this_obj.pose.bones[bone].custom_shape_scale_xyz=(0.5,0.5,0.5)
        this_obj.pose.bones[bone].use_custom_shape_bone_size = False
        
        if "upper_arm" in bone:
            if ".L" in bone:
                this_obj.pose.bones[bone].custom_shape_translation=(-0.05,0.0,0.0)
                this_obj.pose.bones[bone].custom_shape_rotation_euler=(0,-1.5708,0)
                this_obj.pose.bones[bone].custom_shape_transform = this_obj.pose.bones["MCH-upper_arm_parent_widget.L"]
            else:
                this_obj.pose.bones[bone].custom_shape_translation=(0.05,0.0,0.0)
                this_obj.pose.bones[bone].custom_shape_rotation_euler=(0,-1.5708,0)
                this_obj.pose.bones[bone].custom_shape_transform = this_obj.pose.bones["MCH-upper_arm_parent_widget.R"]
        else:
            if ".L" in bone:
                this_obj.pose.bones[bone].custom_shape_translation=(0.1,0,0)
                this_obj.pose.bones[bone].custom_shape_rotation_euler=(-0.0820305, -1.5708, 0)
                this_obj.pose.bones[bone].custom_shape_transform = this_obj.pose.bones["MCH-thigh_parent_widget.L"]
            else:
                this_obj.pose.bones[bone].custom_shape_translation=(-0.1,0,0)
                this_obj.pose.bones[bone].custom_shape_rotation_euler=(-0.0820305, 1.5708, 0)
                this_obj.pose.bones[bone].custom_shape_transform = this_obj.pose.bones["MCH-thigh_parent_widget.R"]
        
    # ENABLE CONSTRAINTS AGAIN HERE
    if use_head_tracker:
        this_obj.pose.bones["MCH-head-controller-parent"].constraints[0].enabled = True
    this_obj.pose.bones["MCH-forearm_tweak-pin.parent.L"].constraints[0].enabled = True
    this_obj.pose.bones["MCH-forearm_tweak-pin.parent.R"].constraints[0].enabled = True
    this_obj.pose.bones["MCH-shin_tweak-pin.parent.L"].constraints[0].enabled = True
    this_obj.pose.bones["MCH-shin_tweak-pin.parent.R"].constraints[0].enabled = True
    this_obj.pose.bones["MCH-torso.parent"].constraints[0].enabled = True
    
    # Deselect everything, we're done.
    for bone in bpy.context.active_object.pose.bones:
        bone.bone.select = False
        
    # EDITING ui.py TEXT FILE --------------------------------------------
    rig_file = bpy.data.texts[original_name+'_ui.py'] # Rig script for this char in question
    
    # Convert it to text
    rig_text = rig_file.as_string()
    complete_rig_text = rig_text
    # My disclaimer, out of respect for modifying Rigify core's script
    rig_text_disclaimer = """
# This RigUI script has been modified by Llama for use with Genshin Impact characters using a custom-made rig. Any issues arising as a result of these modifications are not indicative of Rigify's original functionalities.
# Rigify's authors bear no responsibility for issues/errors resulting from these modifications. Additionally, these modifications have been made to improve the custom-made rigs for Genshin Impact characters.
# Attempting to use this script with characters/models/skeletons it was not intended for could yield improper or erroneous results, for which neither Rigify's development team nor I are responsible.

# If you are seeing this disclaimer on a Hoyoverse character made with the proper addons, run this as needed (e.g., after appending to build the rig layers).
# Do NOT, however, attempt to use this rig in a version of Blender other than the one it was made in. (3.6.X rigs will NOT work adequately in 4.X or beyond, and 4.X rigs will not work in versions before 4.0).
"""
    
    # MODIFICATIONS to the text file are made here:
    # Get the ID of this char's rig ui script.
    rig_char_id = rig_text.split("rig_id = \"")[1].split("\"")[0]
    
    def make_layer_str(text, layer, version):
        string3 = "row.prop(context.active_object.data, 'layers', index="+str(layer)+", toggle=True, text='"+text+"')"
        string4 = "row.prop(collection[\""+text+"\"], 'is_visible', toggle=True, text='"+text+"')"
        
        if version == 4:
            return string4
        else:
            return string3
    
    # String object of the actual layers
    def layers_to_generate(vers):
        str = "\n            row=col.row()\n            "+make_layer_str("Tweaks", 2, vers)+"\n            row=col.row()\n            "+make_layer_str("Pivots & Pins", 19, vers)+"\n            row = col.row()\n            "+make_layer_str("Offsets", 26, vers)+"\n            row = col.row()\n            "+make_layer_str("Props", 21, vers)+"\n            row = col.row()\n            row.separator()\n            row = col.row()\n            row.separator()\n            row = col.row()\n            "+make_layer_str("Face", 0, vers)+"\n            row = col.row()\n            "+make_layer_str("Torso (IK)", 3, vers)+"\n            row = col.row()\n            "+make_layer_str("Torso (FK)",4,vers)+"\n            row = col.row()\n            "+make_layer_str("Fingers", 5, vers)+"\n            row = col.row()\n            "+make_layer_str("Fingers (Detail)", 6, vers)+"\n            row = col.row()\n            "+make_layer_str("Arm.L (IK)", 7, vers)+"\n            "+make_layer_str("Arm.R (IK)", 10, vers)+"\n            row = col.row()\n            "+make_layer_str("Arm.L (FK)", 8, vers)+"\n            "+make_layer_str("Arm.R (FK)", 11, vers)+"\n            row = col.row()\n            "+make_layer_str("Leg.L (IK)", 13, vers)+"\n            "+make_layer_str("Leg.R (IK)", 16, vers)+"\n            row = col.row()\n            "+make_layer_str("Leg.L (FK)", 14, vers)+"\n            "+make_layer_str("Leg.R (FK)", 17, vers)+"\n            row = col.row()\n            row.separator()\n            row = col.row()\n            row.separator()\n            row = col.row()\n            "+make_layer_str("Root", 28, vers)
        
        if lighting_panel_rig_obj:
            str+="\n            row = col.row()\n            "+make_layer_str("Lighting", 1, vers)
        
        str+="\n            row = col.row()\n            "+make_layer_str("Physics", 20, vers)+"\n            row = col.row()\n            "+make_layer_str("Cage", 24, vers)+"\n            "+make_layer_str("Other", 25, vers)
                
        return str
        
    # Function to add layer to rigUI. This should add it to both 3.6 and 4.0 versions of the UI.
    def generate_rig_layers():
        # Add the physics button to the UI # text=v_str+" rig for " + char_name
        rig_add_layer_code = "\n        layout = self.layout\n        col = layout.column()\n        row = col.row()\n        v_str = \""+bpy.app.version_string+"\"\n        row.label(text=v_str+\" rig for "+char_name.split("Costume")[0]+"\")\n        if not v_str[0] == \"4\" and bpy.app.version_string[0] == \"3\":\n            "+layers_to_generate(3)+"\n        elif v_str[0] == \"4\" and bpy.app.version_string[0] == \"4\":\n            # If you have duplicate armatures of the same character (if you see .001 or similar) in one scene,\n            # Please change the name below to what it is in the Outliner so that you can rig all your characters :)\n            # (It's the green person symbol in your rig)\n            collection = bpy.data.armatures[\""+original_name+"\"].collections\n            "+layers_to_generate(4)+"\n        else:\n            row.label(text=\"ERROR: Version mismatch!\")\n            row = col.row()\n            row.label(text=\"Your rig was made in a version of Blender/Goo Engine that is not compatible!\")\n            row = col.row()\n            row.label(text=\"Please remake your rig for this version!\")"
        cut_rig_layer = rig_text.split("class RigLayers(bpy.types.Panel):")
        separate_draw_func = cut_rig_layer[1].split("def draw(self, context):")
        separate_draw_end = separate_draw_func[1].split("def register():")
        
        merged_layer_code = cut_rig_layer[0]+"class RigLayers(bpy.types.Panel):"+separate_draw_func[0]+"def draw(self, context):"+rig_add_layer_code+"\ndef register():"+separate_draw_end[1]
        
        return merged_layer_code
    
    complete_rig_text = generate_rig_layers()

    # These functions make it easy to quickly write to the text file. Use as needed.
    def generate_string_for_limb_pin(pin_bone, gear_bone, tweak_bone, text):
        str = "\n        if is_selected({'"+pin_bone+"'}):\n            layout.prop(pose_bones['"+tweak_bone+"'], '[\"tweak_pin\"]', text='"+text+"', slider=True)\n        if is_selected({'"+gear_bone+"'}):\n            layout.prop(pose_bones['"+tweak_bone+"'], '[\"tweak_pin\"]', text='"+text+"', slider=True)"
        return str
    
    def generate_string_for_parent_switch(bone):
        str = "\n        if is_selected({'"+bone+"'}):\n            group1 = layout.row(align=True)\n            group2 = group1.split(factor=0.75, align=True)\n            props = group2.operator('pose.rigify_switch_parent_"+rig_char_id+"\', text=\'Parent Switch\', icon=\'DOWNARROW_HLT\')\n            props.bone = \'"+bone+"\'\n            props.prop_bone = \'"+bone+"\'\n            props.prop_id=\'parent_switch\'\n            props.parent_names = '[\"None\", \"root\", \"root.001\", \"root.002\", \"torso\", \"chest\"]'\n            props.locks = (False, False, False)\n            group2.prop(pose_bones['"+bone+"'], '[\"parent_switch\"]', text='')\n            props = group1.operator('pose.rigify_switch_parent_bake_"+rig_char_id+"', text='', icon='ACTION_TWEAK')\n            props.bone = '"+bone+"'\n            props.prop_bone='"+bone+"'\n            props.prop_id='parent_switch'\n            props.parent_names='[\"None\", \"root\", \"root.001\", \"root.002\", \"torso\", \"chest\"]'\n            props.locks = (False, False, False)"
        return str
    # Used for already existing bones (torso and limbs)
    def generate_string_for_ik_switch(bone, prop1, prop2):
        str = "\n        if is_selected({'"+bone+"'}):\n            group1 = layout.row(align=True)\n            group2 = group1.split(factor=0.75, align=True)\n            props = group2.operator('pose.rigify_switch_parent_"+rig_char_id+"\', text=\'Parent Switch\', icon=\'DOWNARROW_HLT\')\n            props.bone = \'"+prop1+"\'\n            props.prop_bone = \'"+prop2+"\'\n            props.prop_id=\'IK_parent\'\n            props.parent_names = '[\"None\", \"root\", \"root.001\", \"root.002\", \"torso\", \"chest\"]'\n            props.locks = (False, False, False)\n            group2.prop(pose_bones['"+prop2+"'], '[\"IK_parent\"]', text='')\n            props = group1.operator('pose.rigify_switch_parent_bake_"+rig_char_id+"', text='', icon='ACTION_TWEAK')\n            props.bone = '"+prop1+"'\n            props.prop_bone='"+prop2+"'\n            props.prop_id='IK_parent'\n            props.parent_names='[\"None\", \"root\", \"root.001\", \"root.002\", \"torso\", \"chest\"]'\n            props.locks = (False, False, False)"
        return str
    
    # because rigify makes the rig ui before i get to it, we have to change this stuff for the torso sliders below.
    def torso_str():
        torso="\n                props.bone = 'torso.002'\n                props.prop_bone = 'torso.002'\n                props.prop_id = 'torso_parent'\n                props.parent_names = '[\"None\", \"Root\"]'\n                props.locks = (False, False, False)\n                group2.prop(pose_bones['torso.002'], '[\"torso_parent\"]', text='')\n                props = group1.operator('pose.rigify_switch_parent_bake_"+rig_char_id+"', text='', icon='ACTION_TWEAK')\n                props.bone = 'torso.002'\n                props.prop_bone = 'torso.002'\n                props.prop_id = 'torso_parent'\n                props.parent_names = '[\"None\", \"Root\"]'\n                props.locks = (False, False, False)"
        return torso
        
    def torso_repair():
        cut = complete_rig_text.split("props = group2.operator('pose.rigify_switch_parent_"+rig_char_id+"', text='Torso Parent', icon='DOWNARROW_HLT')")
        second_str = "if is_selected({'foot_fk.L', 'foot_ik.L', 'thigh_ik_target.L', 'foot_tweak.L', 'shin_tweak.L', 'foot_heel_ik.L', 'thigh_ik.L', 'VIS_thigh_ik_pole.L', 'toe_fk.L', 'shin_fk.L', 'thigh_parent.L', 'foot_spin_ik.L', 'thigh_fk.L', 'toe_ik.L', 'thigh_tweak.L', 'thigh_tweak.L.001', 'shin_tweak.L.001'}):"
        second_half = cut[1]
        new_cut = second_half.split(second_str)
        final = new_cut[1]
        
        merged_text = cut[0]+"props = group2.operator('pose.rigify_switch_parent_"+rig_char_id+"', text='Torso Parent', icon='DOWNARROW_HLT')"+torso_str()+second_str+final
        
        return merged_text
    
    # give this a position in the text file (a string to look for), after that position it'll add the text passed in
    def splice_into_text(divider, text):
        split = complete_rig_text.split(divider)
        return split[0]+divider+text+split[1]
    
    # If head controller, add the rig main controls for it.
    if use_head_tracker:
        complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_parent_switch("head-controller"))
    
    # Make the limb edits   
    # Below is the emergency cut for the torso repair. (WHY rigify?!?!?)

    #complete_rig_text = complete_rig_text.replace("props.bone = 'torso'","props.bone = 'torso.002'").replace("props.prop_bone = 'torso'","props.prop_bone = 'torso.002'").replace("group2.prop(pose_bones['torso'], '[\"torso_parent\"]', text='')","group2.prop(pose_bones['torso.002'], '[\"torso_parent\"]', text='')")
    
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_parent_switch("forearm_tweak-pin.L"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_limb_pin("forearm_tweak-pin.L","upper_arm_parent.L","forearm_tweak.L","Elbow Pin"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_parent_switch("forearm_tweak-pin.R"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_limb_pin("forearm_tweak-pin.R","upper_arm_parent.R","forearm_tweak.R","Elbow Pin"))
    
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_ik_switch("hand_ik_pivot.L","hand_ik.L","upper_arm_parent.L"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_ik_switch("hand_ik_pivot.R","hand_ik.R","upper_arm_parent.R"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_ik_switch("foot_ik_pivot.L","foot_ik.L","thigh_parent.L"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_ik_switch("foot_ik_pivot.R","foot_ik.R","thigh_parent.R"))

    
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_parent_switch("shin_tweak-pin.L"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_limb_pin("shin_tweak-pin.L","thigh_parent.L","shin_tweak.L","Knee Pin"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_parent_switch("shin_tweak-pin.R"))
    complete_rig_text = splice_into_text("num_rig_separators[0] += 1", generate_string_for_limb_pin("shin_tweak-pin.R","thigh_parent.R","shin_tweak.R","Knee Pin"))
    
    # Clear the text from the text block, reassemble it as needed with strings and modifications.
    rig_file.clear() 
    rig_file.write(complete_rig_text)
    rig_file.write(rig_text_disclaimer)
      
       
    # After all text block modifications, run the new edited script.
    ctx = bpy.context.copy()
    ctx['edit_text'] = rig_file
    with bpy.context.temp_override(edit_text=rig_file):
        bpy.ops.text.run_script()
    
    # DONE MODIFYING ui.py FILE --------------------------------------------
    
    
    # if using lighting panel, tie the visiblity of the RGB circle meshes to the visibility of the lighting layer.
    if lighting_panel_rig_obj:
        def drive_visibility_with_prop(obj, path):
            driver_obj = bpy.context.scene.objects[obj]
            driver = driver_obj.driver_add("hide_viewport").driver
            
            driver.type = 'SCRIPTED'
            driver.expression = 'not is_visible'
            
            var = driver.variables.new()
            var.name = "is_visible"
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "ARMATURE"
            var.targets[0].id = armature
            if is_version_4:
                var.targets[0].data_path = path
            else:
                var.targets[0].data_path = "layers[1]"
            
        drive_visibility_with_prop("ColorWheel-Ambient","collections[\"Lighting\"].is_visible")
        drive_visibility_with_prop("ColorWheel-Fresnel","collections[\"Lighting\"].is_visible")
        drive_visibility_with_prop("ColorWheel-Lit","collections[\"Lighting\"].is_visible")
        drive_visibility_with_prop("ColorWheel-RimLit","collections[\"Lighting\"].is_visible")
        drive_visibility_with_prop("ColorWheel-RimShadow","collections[\"Lighting\"].is_visible")
        drive_visibility_with_prop("ColorWheel-Shadow","collections[\"Lighting\"].is_visible")
        drive_visibility_with_prop("ColorWheel-SoftLit","collections[\"Lighting\"].is_visible")
        drive_visibility_with_prop("ColorWheel-SoftShadow","collections[\"Lighting\"].is_visible")
  
    
    # Post modification, Adjustment of bone layers/collections.
    if not is_version_4:
        for x in range(29):
            if x>0:
                bpy.context.object.data.layers[x] = False
                
        # Disable/Enable Rig UI layers we care about
        bpy.context.object.data.layers[0] = True
        bpy.context.object.data.layers[1] = True if lighting_panel_rig_obj else False  # Lighting
        bpy.context.object.data.layers[3] = True
        bpy.context.object.data.layers[4] = False
        bpy.context.object.data.layers[5] = True
        bpy.context.object.data.layers[6] = False
        bpy.context.object.data.layers[7] = True
        bpy.context.object.data.layers[8] = False
        bpy.context.object.data.layers[10] = True
        bpy.context.object.data.layers[11] = False
        bpy.context.object.data.layers[13] = True
        bpy.context.object.data.layers[14] = False
        bpy.context.object.data.layers[16] = True
        bpy.context.object.data.layers[17] = False
        bpy.context.object.data.layers[21] = True
        bpy.context.object.data.layers[28] = True
        bpy.context.object.data.layers[26] = True
    else:            
        bpy.context.object.data.collections["Tweaks"].is_visible = False
        bpy.context.object.data.collections["Pivots & Pins"].is_visible = False
        bpy.context.object.data.collections["Torso (FK)"].is_visible = False
        bpy.context.object.data.collections["Fingers (Detail)"].is_visible = False
        bpy.context.object.data.collections["Arm.L (FK)"].is_visible = False
        bpy.context.object.data.collections["Arm.R (FK)"].is_visible = False
        bpy.context.object.data.collections["Leg.L (FK)"].is_visible = False
        bpy.context.object.data.collections["Leg.R (FK)"].is_visible = False
        bpy.context.object.data.collections["Physics"].is_visible = False
        bpy.context.object.data.collections["Cage"].is_visible = False
        bpy.context.object.data.collections["Other"].is_visible = False
    
    # Send the given bone to its new location for either version. Adjusted for actual layer num.
    # MOVING OF BONES BELOW -------------------------------
    def bone_to_layer(bone, layer, collection, second_coll="None"):
        arm = bpy.context.object
        if bone in arm.data.bones:
            if is_version_4:
                if collection == "Other":
                    bpy.context.object.data.collections[collection].assign(bpy.context.object.data.bones[bone])
                else:
                    bpy.context.object.data.collections[collection].assign(bpy.context.object.data.bones[bone])
                    bpy.context.object.data.collections["Other"].unassign(bpy.context.object.data.bones[bone])
                    if second_coll != "None":
                        bpy.context.object.data.collections[second_coll].assign(bpy.context.object.data.bones[bone])                                                                                                
            else:
                move_bone(bone,layer)
                
    # Since we've looped through ever 4.0 bone to place in 'other' above, we'll have to do so as well for 3.6
    if not is_version_4:
        for bone in bpy.context.active_object.pose.bones:
            bone_to_layer(bone.name, 25, "Other")            
    
    loop_arm = bpy.context.object.data
    for bone in loop_arm.bones:
        if "tweak" in bone.name and "MCH" not in bone.name and "pin" not in bone.name:
            bone_to_layer(bone.name, 2, "Tweaks")  
    
    # Moving to Tweaks (werent catched in loop)
    bone_to_layer("tweak_spine", 2, "Tweaks") 
    bone_to_layer("tweak_spine.001", 2, "Tweaks") 
    bone_to_layer("tweak_spine.002", 2, "Tweaks") 
    bone_to_layer("tweak_spine.003", 2, "Tweaks") 
    bone_to_layer("tweak_spine.004", 2, "Tweaks") 
    bone_to_layer("tweak_spine.005", 2, "Tweaks") 
    # MOVING PIVOTS AND PINS
    bone_to_layer("torso_pivot.002", 19, "Pivots & Pins") 
    bone_to_layer("forearm_tweak-pin.L", 19, "Pivots & Pins") 
    bone_to_layer("hand_ik_pivot.L", 19, "Pivots & Pins") 
    bone_to_layer("hand_ik_pivot.R", 19, "Pivots & Pins") 
    bone_to_layer("forearm_tweak-pin.R", 19, "Pivots & Pins") 
    bone_to_layer("shin_tweak-pin.L", 19, "Pivots & Pins") 
    bone_to_layer("shin_tweak-pin.R", 19, "Pivots & Pins") 
    bone_to_layer("foot_ik_pivot.L", 19, "Pivots & Pins") 
    bone_to_layer("foot_ik_pivot.R", 19, "Pivots & Pins") 
    
    # MOVING FACE
    bone_to_layer("plate-settings", 0, "Face")        
    bone_to_layer("plate-border", 0, "Face")        
    bone_to_layer("Plate", 0, "Face")        
    bone_to_layer("eyetrack", 0, "Face")
    if use_head_tracker:
        bone_to_layer("head-controller", 0, "Face")  
    else:
        bone_to_layer("head-controller", 25, "Other") 
    bone_to_layer("eyetrack_L", 0, "Face")        
    bone_to_layer("eyetrack_R", 0, "Face")  
    
    # Disable selection of face bone
    selected_bone = faceplate_arm.pose.bones["Plate"]
    selected_bone.bone.hide_select = True    
    
    bone_to_layer("Brow-Trouble-R-Control", 0, "Face")        
    bone_to_layer("Brow-Trouble-L-Control", 0, "Face")        
    bone_to_layer("Brow-Shy-R-Control", 0, "Face")        
    bone_to_layer("Brow-Shy-L-Control", 0, "Face")        
    bone_to_layer("Brow-Angry-R-Control", 0, "Face")        
    bone_to_layer("Brow-Angry-L-Control", 0, "Face")        
    bone_to_layer("Brow-Smily-R-Control", 0, "Face")        
    bone_to_layer("Brow-Smily-L-Control", 0, "Face")        
    bone_to_layer("Brow-R-Control", 0, "Face")        
    bone_to_layer("Brow-L-Control", 0, "Face")        
    
    bone_to_layer("Eye-Up-Control", 0, "Face")        
    bone_to_layer("Eye-Tired-Control", 0, "Face")        
    bone_to_layer("Eye-Wail-Control", 0, "Face")        
    bone_to_layer("Eye-Ha-Control", 0, "Face")        
    bone_to_layer("Wink-Control-R", 0, "Face")        
    bone_to_layer("Eye-WinkA-Control", 0, "Face")        
    bone_to_layer("Eye-WinkB-Control", 0, "Face")        
    bone_to_layer("Eye-WinkC-Control", 0, "Face")        
    bone_to_layer("Wink-Control-L", 0, "Face")        
    bone_to_layer("Eye-Down-Control", 0, "Face")        
    bone_to_layer("Eye-Jito-Control", 0, "Face")        
    bone_to_layer("Eye-Hostility-Control", 0, "Face")        
    bone_to_layer("Eye-LowerEyelid-Control", 0, "Face")        
    bone_to_layer("Eye-Star-Control", 0, "Face")        
    bone_to_layer("Eye-Pupil-Control", 0, "Face")        
    
    bone_to_layer("Mouth-Control", 0, "Face")        
    bone_to_layer("Mouth-Smile1-Control", 0, "Face")        
    bone_to_layer("Mouth-Smile2-Control", 0, "Face")        
    bone_to_layer("Mouth-Angry1-Control", 0, "Face")        
    bone_to_layer("Mouth-Angry2-Control", 0, "Face")        
    bone_to_layer("Mouth-Angry3-Control", 0, "Face")        
    bone_to_layer("Mouth-Fury1-Control", 0, "Face")        
    bone_to_layer("Mouth-Doya1-Control", 0, "Face")        
    bone_to_layer("Mouth-Doya2-Control", 0, "Face")        
    bone_to_layer("Mouth-Pero1-Control", 0, "Face")        
    bone_to_layer("Mouth-Pero2-Control", 0, "Face")        
    bone_to_layer("Mouth-Neko1-Control", 0, "Face")        
    bone_to_layer("Mouth-Default-Control", 0, "Face")  
    
    # Moving Torso
    bone_to_layer("head", 3, "Torso (IK)")  
    bone_to_layer("neck", 3, "Torso (IK)")  
    bone_to_layer("chest", 3, "Torso (IK)")  
    bone_to_layer("torso", 3, "Torso (IK)")  
    bone_to_layer("torso.001", 26, "Offsets")  
    bone_to_layer("torso.002", 26, "Offsets")  
    bone_to_layer("hips", 3, "Torso (IK)")  
    
    bone_to_layer("spine_fk.003", 4, "Torso (FK)")  
    bone_to_layer("spine_fk.002", 4, "Torso (FK)")  
    bone_to_layer("spine_fk.001", 4, "Torso (FK)")  
    bone_to_layer("spine_fk", 4, "Torso (FK)")  
    
    # Moving Fingers
    bone_to_layer("thumb.01_master.L", 5, "Fingers")  
    bone_to_layer("thumb.01_master.R", 5, "Fingers")  
    bone_to_layer("f_index.01_master.L", 5, "Fingers")  
    bone_to_layer("f_index.01_master.R", 5, "Fingers")  
    bone_to_layer("f_middle.01_master.L", 5, "Fingers")  
    bone_to_layer("f_middle.01_master.R", 5, "Fingers")  
    bone_to_layer("f_ring.01_master.L", 5, "Fingers")  
    bone_to_layer("f_ring.01_master.R", 5, "Fingers")  
    bone_to_layer("f_pinky.01_master.L", 5, "Fingers")  
    bone_to_layer("f_pinky.01_master.R", 5, "Fingers")  
    
    bone_to_layer("thumb.01.L", 6, "Fingers (Detail)")  
    bone_to_layer("thumb.01.R", 6, "Fingers (Detail)")  
    bone_to_layer("thumb.02.L", 6, "Fingers (Detail)")  
    bone_to_layer("thumb.02.R", 6, "Fingers (Detail)")  
    bone_to_layer("thumb.03.L", 6, "Fingers (Detail)")  
    bone_to_layer("thumb.03.R", 6, "Fingers (Detail)")  
    bone_to_layer("thumb.01.L.001", 6, "Fingers (Detail)")  
    bone_to_layer("thumb.01.R.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.01.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.01.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.02.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.02.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.03.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.03.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.01.L.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_index.01.R.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.01.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.01.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.02.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.02.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.03.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.03.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.01.L.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_middle.01.R.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.01.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.01.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.02.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.02.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.03.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.03.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.01.L.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_ring.01.R.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.01.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.01.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.02.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.02.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.03.L", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.03.R", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.01.L.001", 6, "Fingers (Detail)")  
    bone_to_layer("f_pinky.01.R.001", 6, "Fingers (Detail)") 

    if lighting_panel_rig_obj:
        bone_to_layer("Lighting Panel", 1, "Lighting")
        bone_to_layer("Fresnel", 1, "Lighting")
        bone_to_layer("Ambient", 1, "Lighting")
        bone_to_layer("SoftLit", 1, "Lighting")
        bone_to_layer("Lit", 1, "Lighting")  # Sharp Lit
        bone_to_layer("SoftShadow", 1, "Lighting")
        bone_to_layer("Shadow", 1, "Lighting")  # Sharp Shadow
        bone_to_layer("RimShadow", 1, "Lighting")
        bone_to_layer("Rim Lit", 1, "Lighting")
        bone_to_layer("RimX", 1, "Lighting")
        bone_to_layer("RimY", 1, "Lighting")
        bone_to_layer("RimLitPin", 1, "Lighting")
        bone_to_layer("ShadowPin", 1, "Lighting")
        bone_to_layer("LitPin", 1, "Lighting")
        bone_to_layer("AmbientPin", 1, "Lighting")
        bone_to_layer("RimShadowPin", 1, "Lighting")
        bone_to_layer("SoftShadowPin", 1, "Lighting")
        bone_to_layer("SoftLitPin", 1, "Lighting")
        bone_to_layer("FresnelPin", 1, "Lighting")

    # Pass in a list, all of those bones will be moved accordingly.
    def fast_bone_move(bone_list, layer, collection):
        for bone in bone_list:
            bone_to_layer(bone, layer, collection)
    
    # Refactoring old bone move functionalities
    list_move_to_other = ["+UpperArmTwistA02.L","+UpperArmTwistA01.L","+UpperArmTwistA01.R","+UpperArmTwistA02.R","eye.R","eye.L","+ToothBone D A01","+ToothBone U A01","+ToothBone A A01"]
    fast_bone_move(list_move_to_other, 25, "Other")
    
    if toe_bones_exist:
        bone_to_layer("toe_ik.L", 13, "Leg.L (IK)")
        bone_to_layer("toe_ik.R", 16, "Leg.R (IK)")
    else:
        bone_to_layer("toe_ik.L", 25, "Other")
        bone_to_layer("toe_ik.R", 25, "Other")
    
    if use_arm_ik_poles:
        bone_to_layer("upper_arm_ik.L", 25, "Other")
        bone_to_layer("upper_arm_ik.R", 25, "Other")
    else:
        bone_to_layer("upper_arm_ik.L", 7, "Arm.L (IK)")
        bone_to_layer("upper_arm_ik.R", 10, "Arm.R (IK)")
    
    if use_leg_ik_poles:
        bone_to_layer("thigh_ik.L", 25, "Other")
        bone_to_layer("thigh_ik.R", 25, "Other")
    else:
        bone_to_layer("thigh_ik.L", 13, "Leg.L (IK)")
        bone_to_layer("thigh_ik.R", 16, "Leg.R (IK)")
        
    try:
        bone_to_layer("+EyeBone L A01.001", 25, "Other")
        bone_to_layer("+EyeBone R A01.001", 25, "Other")
    except:
        pass
        
    if not use_head_tracker:
        bone_to_layer("head-controller", 25, "Other")
        
    if no_eyes:
        bone_to_layer("eyetrack",25,"Other")
        bone_to_layer("eyetrack_L",25,"Other")
        bone_to_layer("eyetrack_R",25,"Other")
           
    # New bones, post append 
    list_to_send_other = ["MCH-thigh_ik_target_sub.L","MCH-thigh_ik_target_sub.R","MCH-foot_ik_pivot.L","MCH-foot_ik_pivot.R","MCH-hand_ik_pivot.L","MCH-hand_ik_pivot.R","MCH-hand_ik_wrist.L","MCH-hand_ik_wrist.R","MCH-torso_pivot.002","shoulder_driver.R","shoulder_driver.L","MCH-shoulder_follow.R","MCH-shoulder_follow.L"]
    
    fast_bone_move(list_to_send_other,25,"Other")
    
    send_to_pivots = ["foot_ik_pivot.L","foot_ik_pivot.R","hand_ik_pivot.L","hand_ik_pivot.R","torso_pivot.002","forearm_tweak-pin.L","forearm_tweak-pin.R","shin_tweak-pin.L","shin_tweak-pin.R"]
    fast_bone_move(send_to_pivots, 19, "Pivots & Pins")
    
    bone_to_layer("root.002", 28, "Root")
    bone_to_layer("root.001", 26, "Offsets")
    bone_to_layer("root", 26, "Offsets")
    
    bone_to_layer("hand_ik.L",7,"Arm.L (IK)")
    bone_to_layer("hand_ik_wrist.L",26,"Offsets")
    bone_to_layer("upper_arm_parent.L",[7,8],"Arm.L (IK)","Arm.L (FK)")
    bone_to_layer("upper_arm_ik_target.L",7,"Arm.L (IK)")
    bone_to_layer("shoulder.L",[7,8],"Arm.L (IK)","Arm.L (FK)")
    
    bone_to_layer("hand_ik.R",10,"Arm.R (IK)")
    bone_to_layer("upper_arm_parent.R",[10,11],"Arm.R (IK)","Arm.R (FK)")
    bone_to_layer("hand_ik_wrist.R",26,"Offsets")
    bone_to_layer("upper_arm_ik_target.R",10,"Arm.R (IK)")
    bone_to_layer("shoulder.R",[10,11],"Arm.R (IK)","Arm.R (FK)")
    
    bone_to_layer("upper_arm_fk.L",8,"Arm.L (FK)")
    bone_to_layer("forearm_fk.L",8,"Arm.L (FK)")
    bone_to_layer("hand_fk.L",8,"Arm.L (FK)")
    
    bone_to_layer("upper_arm_fk.R",11,"Arm.R (FK)")
    bone_to_layer("forearm_fk.R",11,"Arm.R (FK)")
    bone_to_layer("hand_fk.R",11,"Arm.R (FK)")
    
    bone_to_layer("foot_ik.L",13,"Leg.L (IK)")
    bone_to_layer("thigh_parent.L",[13,14],"Leg.L (IK)","Leg.L (FK)")
    bone_to_layer("thigh_ik_target.L",13,"Leg.L (IK)")
    bone_to_layer("foot_ik_sub.L",26,"Offsets")
    bone_to_layer("foot_spin_ik.L",13,"Leg.L (IK)")
    bone_to_layer("foot_heel_ik.L",13,"Leg.L (IK)")
    
    bone_to_layer("thigh_fk.L",14,"Leg.L (FK)")
    bone_to_layer("shin_fk.L",14,"Leg.L (FK)")
    bone_to_layer("foot_fk.L",14,"Leg.L (FK)")
    bone_to_layer("toe_fk.L",14,"Leg.L (FK)")
    
    bone_to_layer("foot_ik.R",16,"Leg.R (IK)")
    bone_to_layer("thigh_parent.R",[16,17],"Leg.R (IK)","Leg.R (FK)")    
    bone_to_layer("thigh_ik_target.R",16,"Leg.R (IK)")
    bone_to_layer("foot_ik_sub.R",26,"Offsets")
    bone_to_layer("foot_spin_ik.R",16,"Leg.R (IK)")
    bone_to_layer("foot_heel_ik.R",16,"Leg.R (IK)")
    
    bone_to_layer("thigh_fk.R",17,"Leg.R (FK)")
    bone_to_layer("shin_fk.R",17,"Leg.R (FK)")
    bone_to_layer("foot_fk.R",17,"Leg.R (FK)")
    bone_to_layer("toe_fk.R",17,"Leg.R (FK)")
    
    bone_to_layer("breast.L",20,"Physics")
    bone_to_layer("breast.R",20,"Physics")
    
    bone_to_layer("prop.L",21,"Props")
    bone_to_layer("prop.R",21,"Props")
    
    def loop_place_physics():
        if is_version_4:
            armature = bpy.context.object.data
            collections = armature.collections        
            
            for bone in armature.bones:
                # The gods of the universe have blessed us with every physics bone starting with "+". We just do some extra filtering and we got what we need.
                if bone.name[0] == "+" and "Twist" not in bone.name and "ToothBone" not in bone.name and "EyeBone" not in bone.name:
                    bone_to_layer(bone.name,20,"Physics")
        else:
            for bone in bpy.context.active_object.pose.bones:
                if bone.name[0] == "+" and "Twist" not in bone.name and "ToothBone" not in bone.name and "EyeBone" not in bone.name:
                    bone_to_layer(bone.name,20,"Physics")

    loop_place_physics()
    
    def loop_place_def():
        # Handpicked bones to serve as the def layer.
        list_custom_skel = ["DEF-thigh.L", "DEF-thigh.R","DEF-shin.L","DEF-shin.R","DEF-foot.L","DEF-foot.R","DEF-spine.001","DEF-spine.002","DEF-spine.003","DEF-spine.004","DEF-spine.006","+UpperArmTwistA02.L","+UpperArmTwistA02.R","DEF-forearm.L","DEF-forearm.R","DEF-hand.R","DEF-hand.L","DEF-shoulder.R","DEF-shoulder.L"]
        
        for bone in list_custom_skel:
            bone_to_layer(bone,24,"Cage")
        
        # Otherwise, anything picked up by VG scan, enable below and disable above.
        #for bone in armature.bones:
        #    if bone.name in vertex_groups_list:
        #        bone_to_layer(bone.name,24,"Cage")

        
    loop_place_def()

    # MOVING OF BONES END -------------------------------    
    
def setup_neck_and_head_follow(neck_follow_value, head_follow_value):
    bpy.context.object.pose.bones["torso"]["neck_follow"] = neck_follow_value
    bpy.context.object.pose.bones["torso"]["head_follow"] = head_follow_value


# Make it so that the finger scale controls can be scaled on the X axis to curl in just the fingertips instead of the entire finger.
def setup_finger_scale_controls_on_x_axis_to_curl_just_the_fingertips(rigified_rig):
    bpy.ops.object.mode_set(mode='POSE')

    for oDrv in rigified_rig.animation_data.drivers:
        for variable in oDrv.driver.variables:
            for target in variable.targets:
                if ".03" in oDrv.data_path and target.data_path[-7:] == "scale.y":
                    target.data_path = target.data_path[:-1] + "x"


    fingerlist = ["thumb.01_master", "f_index.01_master", "f_middle.01_master", "f_ring.01_master", "f_pinky.01_master"]
    for side in [".L", ".R"]:
        for bone in fingerlist:
            rigified_rig.pose.bones[bone + side].lock_scale[0] = False


# Let's 'exclude' that wgt collection: https://blenderartists.org/t/disable-exlude-from-view-layer-in-collection/1324744
def searchForLayerCollection(layerColl, coll_name):
    found = None
    if (layerColl.name == coll_name):
        return layerColl
    for layer in layerColl.children:
        found = searchForLayerCollection(layer, coll_name)
        if found:
            return found


def searchForParentLayerCollection(layerColl, coll_name):
    found = None
    for layer in layerColl.children:
        if (layer.name == coll_name):
            return layerColl
        found = searchForParentLayerCollection(layer, coll_name)
        if found:
            return found


def disable_collection(collection_name):
    view_layer_collection = bpy.context.view_layer.layer_collection

    layer_collection_to_disable = searchForLayerCollection(view_layer_collection, collection_name)
    if layer_collection_to_disable:
        layer_collection_to_disable.exclude = True
        return True
    return False


def move_collection_into_collection(source, destination, collection):  
    destination.children.link(collection)
    source.children.unlink(collection)
