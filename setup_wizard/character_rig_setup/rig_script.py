# Authors: enthralpy, Llama.jpg
# Setup Wizard Integration by michael-gh1

import bpy
import os
from mathutils import Color, Vector
from math import pi

def rig_character(
        file_path, 
        disallow_arm_ik_stretch, 
        disallow_leg_ik_stretch,
        use_arm_ik_poles,
        use_leg_ik_poles,
        add_child_of_constraints,
        use_head_tracker,
        meshes_joined=False):
    
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
                    bpy.ops.transform.resize(override, value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    bpy.ops.object.vertex_group_deselect()
                elif transform_type == "TRANSLATE":
                    bpy.ops.transform.translate(override, value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
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
                bpy.ops.transform.resize(override, value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.ops.object.vertex_group_deselect()
            elif transform_type == "TRANSLATE":
                bpy.ops.transform.translate(override, value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
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
                bpy.ops.transform.resize(override, value=(transformation_1), orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.ops.object.vertex_group_deselect()
            elif transform_type == "TRANSLATE":
                bpy.ops.transform.translate(override, value=transformation_1, orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
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
    create_shape_key("Body", False, "pupil-pushback-R", "CURSOR", ["+EyeBone R A02"], "TRANSLATE", (0, 0.00703, 0), (1.1,1.1,1.1),use_eye_1=True) # 0.0069, 70
    create_shape_key("Body", False, "pupil-pushback-L", "CURSOR", ["+EyeBone L A02"], "TRANSLATE", (0, 0.00703, 0), (1.1,1.1,1.1),use_eye_1=True)

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
            
    #Aw shit here we go again.  This second loop is for making it possible to symmetrize pose bones properly.
    for bone in bones_list:
        if ".L" in bone.name: 
            whee = bone.name[:-2] + ".R"
            armature.edit_bones[bone.name].roll = -armature.edit_bones[whee].roll

    armature.edit_bones["shoulder.L"].roll += 3.14
    armature.edit_bones["shoulder.R"].roll -= 3.14        


                                    
                                                                                                                                
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
        metapose.bones[f"{bone_name}.01.L"].rigify_parameters.primary_rotation_axis = '-Z'
        metapose.bones[f"{bone_name}.01.R"].rigify_parameters.primary_rotation_axis = 'Z'
                                                                               
    metapose.bones["thumb.01.L"].rigify_parameters.primary_rotation_axis = '-X'
    metapose.bones["thumb.01.R"].rigify_parameters.primary_rotation_axis = '-X'                                                                           
                                          

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

    obs = [bpy.data.objects[rigifyr.name], bpy.data.objects[newrig]]
    c={}
    c["object"] = bpy.data.objects[rigifyr.name]
    c["active_object"] = bpy.data.objects[rigifyr.name]
    c["selected_objects"] = obs
    c["selected_editable_objects"] = obs
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.join(c)


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
    def move_into_collection(object,collection):
        
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

    # If it exists, gets rid of the default collection.
    camera_coll = bpy.data.collections.get("Collection")
    if camera_coll:
        bpy.data.collections.remove(camera_coll,do_unlink=True)

    # Let's 'exclude' that wgt collection: https://blenderartists.org/t/disable-exlude-from-view-layer-in-collection/1324744
    def recurLayerCollection(layerColl):
        found = None
        if (layerColl.name == "wgt"):
            return layerColl
        for layer in layerColl.children:
            found = recurLayerCollection(layer)
            if found:
                return found
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection)
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

    # Disable all rig ui layers except the face (where all the extra bones are)
    for x in range(29):
        if x>0:
            bpy.context.object.data.layers[x] = False

    # Function to automatically move a bone (if it exists) to the specified bone layer        
    def move_bone(bone_name,to_layer):
        armature =  bpy.context.active_object
        armature_data = armature.data
        
        if bone_name in armature_data.bones:
            bone = armature_data.bones[bone_name]
            
            # Set to true only where in bone layer we care about
            bone.layers = [i == to_layer-1 for i in range(32)]  # Whatever BL is, -1.

    # Move bones to this layer
    move_bone("+UpperArmTwistA02.L",23)    
    move_bone("+UpperArmTwistA01.L",23)    
    move_bone("+UpperArmTwistA01.R",23)    
    move_bone("+UpperArmTwistA02.R",23)    
    move_bone("eye.R",23)    
    move_bone("eye.L",23)    
    move_bone("eye2.L",23)    
    move_bone("eye2.R",23)    
    move_bone("+ToothBone D A01",23)
    move_bone("+ToothBone U A01",23)
    move_bone("+ToothBone A A01",23)

    move_bone("toe_ik.L",23)
    move_bone("toe_ik.R",23)

    if(use_arm_ik_poles):
        move_bone("upper_arm_ik.L",23)
        move_bone("upper_arm_ik.R",23)
        move_bone("upper_arm_parent.R",23)
        move_bone("upper_arm_parent.L",23)
    if(use_leg_ik_poles):    
        move_bone("thigh_ik.L",23)
        move_bone("thigh_ik.R",23)
        move_bone("thigh_parent.R",23)
        move_bone("thigh_parent.L",23)

    # Put away every other bone to the physics layer (22)
    for bone in bpy.context.active_object.data.bones:
        if bone.layers[0]:  # Check if the bone is on layer face
            move_bone(bone.name, 22)  # Move the bone to layer 23
            
    # Let's append our root_shape custom bones
    path_to_file = file_path + "/Collection"

    # Bring in our collections: root shapes, face rig, and the eye rig
    bpy.ops.wm.append(filename='append_Face Plate', directory=path_to_file)

    bpy.ops.wm.append(filename='append_Root', directory=path_to_file)

    bpy.ops.wm.append(filename='append_Eyes', directory=path_to_file)

    this_obj = None
    for obj in bpy.data.objects:
        if "Rig" in obj.name:
            this_obj = obj

    this_obj.pose.bones["root"].custom_shape = bpy.data.objects["root plate"]
    this_obj.pose.bones["head"].custom_shape_scale_xyz = (1.5,1.5,1.5)

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

    this_obj.pose.bones["torso"].custom_shape = bpy.data.objects["torso-circle"]
    this_obj.pose.bones["chest"].custom_shape = bpy.data.objects["WGT-"+original_name+"_neck"]

    this_obj.pose.bones["torso"].custom_shape_scale_xyz = (0.7,0.63,0.63)
    this_obj.pose.bones["hips"].custom_shape_scale_xyz = (1.39,0.834,1.39)
    this_obj.pose.bones["chest"].custom_shape_scale_xyz = (0.78,0.78,0.78)
    this_obj.pose.bones["chest"].custom_shape_translation = (0.0,0.0,0.025)

    this_obj.pose.bones["foot_heel_ik.L"].custom_shape_translation = (0.0,0.06,0.0)
    this_obj.pose.bones["foot_heel_ik.R"].custom_shape_translation = (0.0,0.06,0.0)

    this_obj.pose.bones["foot_spin_ik.R"].custom_shape_translation = (0.0,-0.05,0.02)
    this_obj.pose.bones["foot_spin_ik.L"].custom_shape_translation = (0.0,-0.05,0.02)

    this_obj.pose.bones["toe_ik.L"].custom_shape_translation = (0.0,0.06,0.00)
    this_obj.pose.bones["toe_ik.R"].custom_shape_translation = (0.0,0.06,0.00)
    this_obj.pose.bones["toe_ik.L"].custom_shape_scale_xyz = (0.781,0.781,0.350)
    this_obj.pose.bones["toe_ik.R"].custom_shape_scale_xyz = (0.781,0.781,0.350)

    this_obj.pose.bones["hand_ik.R"].custom_shape_translation = (0.02,0.0,0.00)
    this_obj.pose.bones["hand_ik.L"].custom_shape_translation = (-0.02,0.0,0.00)

    this_obj.pose.bones["palm.L"].custom_shape_scale_xyz = (1.2,1.2,1.2)
    this_obj.pose.bones["palm.R"].custom_shape_scale_xyz = (1.2,1.2,1.2)


    # Merge the armatures; go into object mode and make sure nothing is selected
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    # Select custom face armature
    face_rig_obj = bpy.data.objects.get("facerig")
    if face_rig_obj:
        face_rig_obj.select_set(True)
        
    # Select eye rig    
    eye_rig_obj = bpy.data.objects.get("eyerig")
    if eye_rig_obj:
        eye_rig_obj.select_set(True)
            
    # Select char armature
    if our_char:
        our_char.select_set(True)

    # Join them
    bpy.ops.object.join()

    # Select the object then access it's rig (its obj data)
    ob = bpy.data.objects[char_name+"Rig"]
    armature = ob.data

    # In edit mode, select platebone and head controller and set their parent bones.
    bpy.ops.object.mode_set(mode='EDIT')
    armature.edit_bones['Plate'].parent = armature.edit_bones['head']
    if(use_head_tracker):
        armature.edit_bones['head-controller'].parent = armature.edit_bones['root']

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
        
    # Functions that loop through skirt bones (Front, Sides, Back) each return a list
    def scan_skirt(area):
        skirt_bones = []
        for edit_bone in armature.edit_bones:
            if validate_skirt(edit_bone.name, area):
                skirt_bones.append(edit_bone.name)

        return skirt_bones

    # On each list, straighten the bone (Straighten on the head)
    front_skirt_bones = scan_skirt("FRONT")
    side_skirt_bones = scan_skirt("SIDE")
    back_skirt_bones = scan_skirt("BACK")

    def straighten_bone(bone_name):
        this_bone = armature.edit_bones[bone_name]
        head = this_bone.head
        this_bone.tail = (head[0],head[1],head[2]-this_bone.length)
        
    for bone in front_skirt_bones:
        straighten_bone(bone)
        
    for bone in side_skirt_bones:
        straighten_bone(bone)
        
    for bone in back_skirt_bones:
        straighten_bone(bone)
        
    # After straightened, For skirt bone 'layers' at depth we need to line them up with the tails of the previous bones in the chain
    def fix_skirt_depth(bone_name):
        backwards_correct = -1
        if " CB " not in bone_name and " CF " not in bone_name:
            backwards_correct = -3
        
        print(bone_name)

        try:
            depth_num = int(bone_name[backwards_correct])
            if depth_num > 1:
                this_bone = armature.edit_bones[bone_name]
                head = this_bone.head
                try:
                    higher_bone = armature.edit_bones[bone_name.replace(str(depth_num), str(depth_num-1))]
                    head.z = higher_bone.tail.z 
                except:
                    pass
        except:
            depth_num = int(bone_name[-1])
            if depth_num > 1:
                this_bone = armature.edit_bones[bone_name]
                head = this_bone.head
                try:
                    higher_bone = armature.edit_bones[bone_name.replace(str(depth_num), str(depth_num-1))]
                    head.z = higher_bone.tail.z 
                except:
                    pass

              

    for bone in front_skirt_bones:
        fix_skirt_depth(bone)
        
    for bone in side_skirt_bones:
        fix_skirt_depth(bone)
        
    for bone in back_skirt_bones:
        fix_skirt_depth(bone)

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

    # Disable selection of face bone
    selected_bone.bone.hide_select = True

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

    # After moving into collection, delete the old empty ones.
    bpy.data.collections.remove(bpy.data.collections.get("append_Root"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Face Plate"),do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections.get("append_Eyes"),do_unlink=True)

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

        if driver:
            influence_driver = co.driver_add("influence").driver
            # DRIVER STUFF
            var = influence_driver.variables.new()
            var.name = "bone"
            var.type = 'TRANSFORMS'
            
            var.targets[0].id = armature
            var.targets[0].bone_target = bone
            var.targets[0].transform_space = 'LOCAL_SPACE'
            var.targets[0].transform_type = trans_rot

            influence_driver.type = 'SCRIPTED'
            influence_driver.expression = expression 

            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
            # END DRIVER STUFF
            
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
                    add_const(bone_name, "Z+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", f_min_x=0, f_max_x=0, f_min_z=calc(-1), f_max_z=calc(1), map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.1), t_max_z=calc(0.1,True))
                elif bone_name[-3] == "2":       
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="X", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.125,True), t_max_z=calc(0))
                elif bone_name[-3] == "3":    
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
            elif " R " in bone_name:
                if bone_name[-1] == "1":       
                    add_const(bone_name, "X+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.75,True), t_max_x=calc(0.75,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "X-", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.3,True), t_max_x=calc(0.3,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", f_min_x=0, f_max_x=0, f_min_z=calc(-1), f_max_z=calc(1), map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.1), t_max_z=calc(0.1,True))
                elif bone_name[-1] == "2":       
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="X", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.125,True), t_max_z=calc(0))
                elif bone_name[-1] == "3":    
                    add_const(bone_name, "Transformation", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0.25,True), t_max_x=calc(-0.25,True), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
        
         # SIDE
        elif area == "SIDE": 
            # Side Left
            if ".L" in bone_name:
                if bone_name[-3] == "1":
                    add_const(bone_name, "X", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", driver=False, map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z",f_min_x=0,f_max_x=0,f_min_z=calc(-1),f_max_z=calc(1),map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.2), t_max_z=calc(0.2))
            
            # Side Right
            elif ".R" in bone_name:
                if bone_name[-3] == "1":
                    add_const(bone_name, "X", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", driver=False, map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z",f_min_x=0,f_max_x=0,f_min_z=calc(-1),f_max_z=calc(1),map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.2), t_max_z=calc(0.2))
            elif " L " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "X", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", driver=False, map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
                    add_const(bone_name, "Z+", "DEF-thigh.L", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", trans_rot="ROT_Z",f_min_x=0,f_max_x=0,f_min_z=calc(-1),f_max_z=calc(1),map_x="X", map_y="Y", map_z="Z", t_min_x=calc(0), t_max_x=calc(0), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(-0.2), t_max_z=calc(0.2))
            
            # Side Right
            elif " R " in bone_name:
                if bone_name[-1] == "1":
                    add_const(bone_name, "X", "DEF-thigh.R", "0.35 + 0.65 * max(0, min(1, (bone*-1)*3))", driver=False, map_x="X", map_y="Y", map_z="Z", t_min_x=calc(-0.15), t_max_x=calc(0.15), t_min_y=calc(0), t_max_y=calc(0), t_min_z=calc(0), t_max_z=calc(0))
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

    # ensure in obj mode

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

    # Enable Rig UI layers we care about
    bpy.context.object.data.layers[0] = True
    bpy.context.object.data.layers[3] = True
    bpy.context.object.data.layers[5] = True
    bpy.context.object.data.layers[7] = True
    bpy.context.object.data.layers[10] = True
    bpy.context.object.data.layers[13] = True
    bpy.context.object.data.layers[16] = True
    bpy.context.object.data.layers[28] = True

    # Disable IK Stretching & Turn on IK Poles. Toggle manually as needed.
    if disallow_leg_ik_stretch:
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.L"]["IK_Stretch"] = 0.0
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.R"]["IK_Stretch"] = 0.0

    if disallow_arm_ik_stretch:
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.L"]["IK_Stretch"] = 0.0
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.R"]["IK_Stretch"] = 0.0
        
    if use_arm_ik_poles:
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.L"]["pole_vector"] = 1.0
        bpy.data.objects[char_name+"Rig"].pose.bones["upper_arm_parent.R"]["pole_vector"] = 1.0
        
    if use_leg_ik_poles:
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.L"]["pole_vector"] = 1.0
        bpy.data.objects[char_name+"Rig"].pose.bones["thigh_parent.R"]["pole_vector"] = 1.0

    bpy.data.objects[char_name+"Rig"].pose.bones["torso"]["head_follow"] = 1.0

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
        add_child_of("hand_ik.L")
        add_child_of("hand_ik.R")
        add_child_of("foot_ik.R")
        add_child_of("foot_ik.L")
        add_child_of("torso")
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

    # We can now make our final bone groups look good!
    def assign_bone_to_group(bone_name, group_name):
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


    # Root BG
    assign_bone_to_group("root", "Root")
    assign_bone_to_group("torso", "Root")
    assign_bone_to_group("hips", "Root")
    assign_bone_to_group("chest", "Root")
    assign_bone_to_group("neck", "Root")
    assign_bone_to_group("head-controller", "Root")
    assign_bone_to_group("head", "Root")

    # Left Arm BG
    assign_bone_to_group("hand_ik.L", "Limbs L")
    assign_bone_to_group("upper_arm_ik_target.L", "Limbs L")
    assign_bone_to_group("shoulder.L", "Limbs L")

    # Right Arm BG
    assign_bone_to_group("hand_ik.R", "Limbs R")
    assign_bone_to_group("upper_arm_ik_target.R", "Limbs R")
    assign_bone_to_group("shoulder.R", "Limbs R")

    # Left Foot BG
    assign_bone_to_group("foot_ik.L", "Limbs L")
    assign_bone_to_group("toe_ik.L", "Limbs L")
    assign_bone_to_group("foot_spin_ik.L", "Limbs L")
    assign_bone_to_group("foot_heel_ik.L", "Limbs L")
    assign_bone_to_group("thigh_ik_target.L", "Limbs L")

    # Right Foot BG
    assign_bone_to_group("foot_ik.R", "Limbs R")
    assign_bone_to_group("toe_ik.R", "Limbs R")
    assign_bone_to_group("foot_spin_ik.R", "Limbs R")
    assign_bone_to_group("foot_heel_ik.R", "Limbs R")
    assign_bone_to_group("thigh_ik_target.R", "Limbs R")

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
        
    change_bone_group_colors('Root',(0,1,0.169),(0.184,1,0.713),(0,0.949,0))
    change_bone_group_colors('Limbs L',(1,0,1),(1,0,0.078),(1,0.812,0))
    change_bone_group_colors('Limbs R',(0,0.839,1),(0.416,0.255,0.902),(0,0.137,0.878))
    change_bone_group_colors('Face',(1,0,0),(0.506,0.902,0.078),(0.094,0.714,0.878))

    try:
        move_bone("+EyeBone L A01.001",23)
        move_bone("+EyeBone R A01.001",23)
    except:
        pass

    if not use_head_tracker:
        move_bone("head-controller",23)
    if no_eyes:
        move_bone("eyetrack",23)
        move_bone("eyetrack_R",23)
        move_bone("eyetrack_L",23)
        
    # Deselect everything, we're done.
    for bone in bpy.context.active_object.pose.bones:
        bone.bone.select = False


# 
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
