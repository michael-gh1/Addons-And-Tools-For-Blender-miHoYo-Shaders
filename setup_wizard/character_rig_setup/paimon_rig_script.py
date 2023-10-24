# Authors: envimm, enthralpy, Llama.jpg
# Setup Wizard Integration by michael-gh1

import bpy


def rig_character(
        file_path, 
        disallow_arm_ik_stretch, 
        disallow_leg_ik_stretch,
        use_arm_ik_poles,
        use_leg_ik_poles,
        add_child_of_constraints,
        use_head_tracker):

    ### IMPORTANT: YOU NEED THE ADDON EXPYKIT AND YOU ALSO NEED TO IMPORT WITH 'Automatic Bone Orientation' TURNED ON UNDER 'Armature' WHEN YOU IMPORT THE FBX.

    import bpy
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
        'Bip001 L Finger0Nub': 'thumb.03.L',
        'Bip001 L Finger1': 'f_index.01.L',
        'Bip001 L Finger11': 'f_index.02.L',
        'Bip001 L Finger1Nub': 'f_index.03.L',
        'Bip001 L Finger2': 'f_middle.01.L',
        'Bip001 L Finger21': 'f_middle.02.L',
        'Bip001 L Finger2Nub': 'f_middle.03.L',
        'Bip001 L Finger3': 'f_ring.01.L',
        'Bip001 L Finger31': 'f_ring.02.L',
        'Bip001 L Finger3Nub': 'f_ring.03.L',
        'Bip001 L Finger4': 'f_pinky.01.L',
        'Bip001 L Finger41': 'f_pinky.02.L',
        'Bip001 L Finger4Nub': 'f_pinky.03.L',
        'Bip001 Neck': 'spine.004', #YO
        'Bip001 Head': 'spine.006', #RUHROH
        'Bip001 R Clavicle': 'shoulder.R',
        'Bip001 R UpperArm': 'upper_arm.R',
        'Bip001 R Forearm': 'forearm.R',
        'Bip001 R Hand': 'hand.R',
        'Bip001 R Finger0': 'thumb.01.R',
        'Bip001 R Finger01': 'thumb.02.R',
        'Bip001 R Finger0Nub': 'thumb.03.R',
        'Bip001 R Finger1': 'f_index.01.R',
        'Bip001 R Finger11': 'f_index.02.R',
        'Bip001 R Finger1Nub': 'f_index.03.R',
        'Bip001 R Finger2': 'f_middle.01.R',
        'Bip001 R Finger21': 'f_middle.02.R',
        'Bip001 R Finger2Nub': 'f_middle.03.R',
        'Bip001 R Finger3': 'f_ring.01.R',
        'Bip001 R Finger31': 'f_ring.02.R',
        'Bip001 R Finger3Nub': 'f_ring.03.R',
        'Bip001 R Finger4': 'f_pinky.01.R',
        'Bip001 R Finger41': 'f_pinky.02.R',
        'Bip001 R Finger4Nub': 'f_pinky.03.R',
        '+EyeBone R A01': 'eye.R',
        '+EyeBone L A01': 'eye.L',   
        '+Breast L A01': 'breast.L',
        '+Breast R A01': 'breast.R', 
        }

    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.context.selected_objects[0].data

    bpy.ops.armature.select_all(action='DESELECT')
    def select_bone(bone):
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        
    # Disconnect the eyes because it'll throw an error if I don't, disconnect the spines so the hip wiggle bone in the rigify rig works properly
    select_bone(armature.edit_bones["+EyeBone L A02"])
    select_bone(armature.edit_bones["+EyeBone R A02"])
    select_bone(armature.edit_bones["Bip001 Spine"])
    select_bone(armature.edit_bones["Bip001 Spine1"])
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

    # fixes upside down shoulders
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

    # Sets up the eyes for the eye rig later
    armature.edit_bones["eye.R"].tail.x = armature.edit_bones["eye.R"].head.x
    armature.edit_bones["eye.L"].tail.x = armature.edit_bones["eye.L"].head.x

    ## Points toe bones in correct direction
    armature.edit_bones['toe.L'].tail.z = 0
    armature.edit_bones['toe.R'].tail.z = 0
    armature.edit_bones['toe.L'].tail.y -= 0.05
    armature.edit_bones['toe.R'].tail.y -= 0.05
            
    bpy.ops.armature.select_all(action='DESELECT')
    try:
        select_bone(armature.edit_bones["breast.L"])
        bpy.ops.armature.symmetrize()
        bpy.ops.armature.select_all(action='DESELECT')

    except Exception:
        pass

    armature.edit_bones["eye.L"].name = "DEF-eye.L"
    armature.edit_bones["eye.R"].name = "DEF-eye.R"
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


    # # Part 4 te eye rig
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')    

    select_bone(rigifyr.data.edit_bones["eye.R"])
    bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False}, TRANSFORM_OT_translate={"value":(-0, -0.0473746, -0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, True, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})


    rigifyr.data.edit_bones["eye.R.001"].name = "eyeTrack.R"

    select_bone(rigifyr.data.edit_bones["eyeTrack.R"])

    bpy.ops.armature.parent_clear(type='DISCONNECT')

    bpy.ops.transform.translate(value=(-0, -0.110905, -0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

    bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={"do_flip_names":False}, TRANSFORM_OT_translate={"value":(-0, -0, -0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(True, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

    rigifyr.data.edit_bones["eyeTrack.R.001"].name = "eyeRoot"

    rigifyr.data.edit_bones["eyeRoot"].tail.x = rigifyr.data.edit_bones["eyeRoot"].head.x = 0

    bpy.ops.armature.select_all(action='DESELECT')

    rigifyr.data.edit_bones['eyeTrack.R'].parent = rigifyr.data.edit_bones['eyeRoot']
    rigifyr.data.edit_bones['eyeRoot'].parent = rigifyr.data.edit_bones['head']


    select_bone(rigifyr.data.edit_bones["eyeTrack.R"])

    bpy.ops.armature.symmetrize()
    rigifyr.data.edit_bones['eyeRoot'].parent = None
            
    rigifyr.data.edit_bones["eyeTrack.R"].roll = 0
    rigifyr.data.edit_bones["eyeTrack.L"].roll = 0
    rigifyr.data.edit_bones["eyeRoot"].roll = 0

    rigifyr.data.edit_bones["+EyeBone L A02"].name = "eye2.L"
    rigifyr.data.edit_bones["+EyeBone R A02"].name = "eye2.R"

    # Symmetrize clothes/hair bones
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


    bpy.ops.object.mode_set(mode='POSE')
    for bone in ['L', 'R']:
        nc = rigifyr.pose.bones['eye.' + bone].constraints.new(type='DAMPED_TRACK')
        nc.target = bpy.data.objects["rigify"]
        nc.subtarget = ('eyeTrack.' + bone)
    nc = rigifyr.pose.bones['eyeRoot'].constraints.new(type='CHILD_OF')
    nc.target = bpy.data.objects["rigify"]
    nc.subtarget = ('head')

    rigifyr.pose.bones["upper_arm_parent.L"]["pole_parent"] = 2
    rigifyr.pose.bones["upper_arm_parent.R"]["pole_parent"] = 2
    rigifyr.pose.bones["thigh_parent.L"]["pole_parent"] = 2
    rigifyr.pose.bones["thigh_parent.R"]["pole_parent"] = 2

    bpy.ops.object.mode_set(mode='OBJECT')
    #change active object to rigifyr

    bpy.context.view_layer.objects.active = bpy.data.objects["rigify"]

    bpy.ops.object.mode_set(mode='OBJECT')

    # This part puts all the main bones I use into the secoond bone layer
    listofbones = ["root", "foot_heel_ik.R", "foot_heel_ik.L", "toe_ik.R", "toe_ik.L", "foot_ik.R", "foot_ik.L", "thigh_ik_target.R", "thigh_ik_target.L", "hips", "torso", "chest", "neck", "head", "eyeRoot", "shoulder.L", "shoulder.R", "upper_arm_fk.L", "upper_arm_fk.R", "forearm_fk.L", "forearm_fk.R", "hand_fk.L", "hand_fk.R", "upper_arm_ik_target.L", "upper_arm_ik_target.R", "hand_ik.R", "hand_ik.L", ]

    for bone in listofbones:
        bpy.context.active_object.pose.bones[bone].bone.layers[1] = True
        
    bpy.data.objects["EyeStar"].hide_viewport = False

    x = original_name.split("_")
    bpy.data.objects["rigify"].name = x[-1] + "Rig"


    # Change any physics bones attached to shoulder to be attached to spine instead bc it's a pain in the ass
    bpy.ops.object.mode_set(mode='EDIT')
    bones = rigifyr.data.edit_bones[:]

    for bone in bones:
        if bone.parent:
            if bone.name not in pre_res and bone.parent.name in ["DEF-shoulder.L", "DEF-shoulder.R"]:
                print(bone)
                #this is a physics bone, so duplicate it.
                bone.parent = rigifyr.data.edit_bones["DEF-spine.004"]
                
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

    bpy.ops.object.mode_set(mode='OBJECT')
    try:
        bpy.context.view_layer.objects.active = bpy.data.objects["Head Driver"] or bpy.data.objects["Head Origin"]
        bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='OBJECT')
    except:
        pass

    rigifyr.pose.bones["upper_arm_parent.L"]["IK_Stretch"] = 0
    rigifyr.pose.bones["upper_arm_parent.R"]["IK_Stretch"] = 0
    rigifyr.pose.bones["thigh_parent.L"]["IK_Stretch"] = 0
    rigifyr.pose.bones["thigh_parent.R"]["IK_Stretch"] = 0
