import maya.cmds as mc
import maya.mel as mel

from importlib import reload
import rjg.libs.file as rFile
import rjg.libs.control.ctrl as rCtrl
reload(rFile)
reload(rCtrl)

def project(body=None, char=None, f_model=None, f_rig=None, f_skel=None, extras=None, f_extras=None, rig_par='head_M_02_CTRL_CNST_GRP', tY=0):
    # reparent face sections to main rig
    mc.group(em=True, name='HIDE_FACE')
    mc.parent('HIDE_FACE', char)
    mc.parent(f_model, 'HIDE_FACE')
    mc.parent(f_rig, 'RIG')
    mc.parent(f_skel, 'SKEL')

    # project the face rig as an always-on blendShape
    #mc.xform(f_skel, t=[0, tY, 0])
    mc.blendShape(f_model, body, name='main_blendshapes', w=[(0, 1.0)], foc=True)

    try:
        mc.select(f_extras, hi=True)
        f_ex_list = mc.ls(selection=True, type='transform')
        mc.group(em=True, name='HIDE_FACE_EXTRAS')
        mc.parent('HIDE_FACE_EXTRAS', 'HIDE_FACE')
        for f in f_ex_list[:0:-1]:
            # if 'brows' in f:
            #     continue
            try:
                f = mc.rename(f, f[len(f_extras):]+'_clone')
                if mc.objExists('Fingernails_clone'):
                    mc.delete('Fingernails_clone')
                    continue
                mc.blendShape(f, f[:-6], name=f[:-6]+'Projection', w=[(0, 1.0)], foc=True)
                mc.parent(f, "HIDE_FACE_EXTRAS")

                mc.hyperShade(f, assign='standardSurface1')
            except Exception as e:
                print(f, ':', e)
    except Exception as e:
        mc.warning(e)

    

    
    # duplcicate the face rig controls and constrain their root to rig_par
    f_rig_name = f_rig
    f_rig = mc.rename(f_rig, f_rig + '_clone')
    f_rig_clone = mc.duplicate(f_rig, renameChildren=True)
    f_rig_clone = mc.rename(f_rig_clone[0], f_rig_name)
    mc.select(f_rig, hierarchy=True)
    f_rig_sel = mc.ls(selection=True, type='transform') #+ mc.ls(selection=True, type='joint') + mc.ls(selection=True, type='follicle')
    mc.select(f_rig_clone, hierarchy=True)
    f_rig_clone_sel = mc.ls(selection=True, type='transform') #+ mc.ls(selection=True, type='joint') + mc.ls(selection=True, type='follicle')
    mc.parentConstraint(rig_par, f_rig_clone_sel[0], mo=True)

    

    # tag incoming controls
    new_controls = mc.listRelatives('face_M', ad=True, type='nurbsCurve')
    for nc in new_controls:
        ct = mc.listRelatives(nc, parent=True)[0]
        rCtrl.tag_as_controller(ct)

    # setup direct connections between the new and original rig and rename 
    for i in range(1, len(f_rig_sel)):
        try:
            mc.connectAttr(f_rig_clone_sel[i] + ".translate", f_rig_sel[i] + ".translate")
            mc.connectAttr(f_rig_clone_sel[i] + ".rotate", f_rig_sel[i] + ".rotate")
            mc.connectAttr(f_rig_clone_sel[i] + ".scale", f_rig_sel[i] + ".scale")

            '''
            for attr in ['Cornea_Vis', 'Pupil_Size']:
                try:
                    mc.connectAttr(f'{f_rig_clone_sel[i]}.{attr}', f'{f_rig_sel[i]}.{attr}')
                    #mc.connectAttr(f_rig_clone_sel[i] + ".translate", f_rig_sel[i] + ".translate")

                except Exception as e:
                    pass
            '''
            og_suff = f_rig_sel[i].split('_')[-1]
            clone_suff = f_rig_clone_sel[i].split('_')[-1]
            mc.rename(f_rig_sel[i], f_rig_sel[i].replace(og_suff, og_suff + '_clone'))
            mc.rename(f_rig_clone_sel[i], f_rig_clone_sel[i].replace(clone_suff, clone_suff[:-1]))
        except Exception as e:
            print(e)
            continue


    #####################################3 
    '''
    Bobo Custom Connection needs
    xxxxxxx  Ribbons
    Influence Constraint Set up
    Cornea Vis

    '''
    #Ribbon FIX
    # Define a dictionary where each rib group has a fixed number of control pins
    rib_group_pin_counts = {
        'Tounge_Right_RIBgrp': 10,
        'Tounge_Left_RIBgrp': 10,
        'R_Brow_Cont_RIBgrp': 6,
        'L_Brow_Cont_RIBgrp': 6,
        'L_Cheek_RIBgrp': 9,
        'L_OuterRing_RIBgrp': 4,
        'L_LipOuter_RIBgrp': 10,
        'L_Lip_RIBgrp': 14,
        'R_Cheek_RIBgrp': 9,
        'R_OuterRing_RIBgrp': 4,
        'R_LipOuter_RIBgrp': 10,
        'R_Lip_RIBgrp': 14,
        'L_Eyelid_RIBgrp': 8,
        'R_Eyelid_RIBgrp': 8
}

    '''
    for rib_group in [ 'Tounge_Right_RIBgrp', 'Tounge_Left_RIBgrp', 'R_Brow_Cont_RIBgrp', 'L_Brow_Cont_RIBgrp', 'L_Cheek_RIBgrp', 'L_OuterRing_RIBgrp', 'L_LipOuter_RIBgrp', 'L_Lip_RIBgrp', 'R_Cheek_RIBgrp', 'R_OuterRing_RIBgrp', 'R_LipOuter_RIBgrp', 'R_Lip_RIBgrp', 'R_Eyelid_RIBgrp', 'L_Eyelid_RIBgrp', ]:
        try:
            base_name = rib_group.replace("_RIBgrp", "")
            print(rib_group)
            
            # Define the ribbon object name
            ribbon_object = f"{base_name}_ribbon"
            dic_num = rib_group_pin_counts.get(rib_group, 10)
            print('get stuff')
            # Get the child objects in the group
            children = mc.listRelatives(rib_group, children=True) or []
            
            # Filter objects that have the suffix "_grp"
            #try:
            #    ctrl_pins = [obj for obj in children if obj.endswith("_grp")]
            #except:
            #    ctrl_pins = 10
            
            # Sort the groups numerically (if they have _PIN_##_grp format)
            #ctrl_pins.sort(key=lambda x: int(x.split("_")[-2]))  
            
            # Determine the number of groups
            #print(ctrl_pins)
            #num_pins = len(ctrl_pins)
            print('get control numbers')
            # Generate the pin locations list (normalized values between 0 and 1)
            #pin_locations = [i / float(num_pins - 1) for i in range(num_pins)]
            
            # List to store world-space positions
            #pin_positions = []

            # Get the world-space positions of the pins using UV coordinates (U varies, V is 0.5)
            #for u in pin_locations:
            #    position = mc.pointOnSurface(ribbon_object, position=True, parameterU=u, parameterV=0.5)
            #    pin_positions.append(position) R_Lip_14_ctrl
            
            # Generate a list for points (formatted like 'NAME_point##_cjnt')
            point_cjnts = [f"{base_name}_{str(i+1).zfill(2)}_cjnt" for i in range(dic_num)]
            ctrl_pins = [f"{base_name}_{str(i+1).zfill(2)}_grp" for i in range(dic_num)]
            ctrlz = [f"{base_name}_{str(i+1).zfill(2)}_ctrl" for i in range(dic_num)]
            print(ctrlz)
            # Get the world position and world rotation (orientation) for each joint
            world_positions = []
            world_orientations = []
            
            for cjnt in point_cjnts:
                # Get world position using xform
                position = mc.xform(cjnt, q=True, ws=True, t=True)
                world_positions.append(position)
                
                # Get world orientation (rotation in world space)
                rotation = mc.xform(cjnt, q=True, ws=True, ro=True)
                world_orientations.append(rotation)
            
            # Now, match the world positions and rotations of the joints to the _grps
            for i, grp in enumerate(ctrl_pins):
                # Match corresponding cjnt's world position and orientation
                target_pos = world_positions[i]
                target_rot = world_orientations[i]
                
                # Apply the world position and orientation to the _grp
                mc.xform(grp, ws=True, t=target_pos)  # Set the world position
                mc.xform(grp, ws=True, ro=target_rot)  # Set the world orientation
            
            # Perform UV pinning on the Ribbon and _grps
            # Iterate through the control pin _grps and pin them to the Ribbon's surface
            #for i, grp in enumerate(ctrl_pins):
            #    u_value = pin_locations[i]  # Use the corresponding U value from the pin locations
            #    v_value = 0.5  # Fixed V value for UV pinning

                # Pin the control pin (group) to the ribbon surface using UV coordinates
            mc.select(f'{ribbon_object}_clone')  # Add ribbon object to selection
            mc.select(ctrl_pins, add=True)
            mc.UVPin()  # Pin the selected objects to the ribbon
            try:
                if rib_group in ['R_Eyelid_RIBgrp']:
                    for obj in ctrlz:
                        parent = mc.listRelatives(obj, parent=True)
                        #if obj == "R_Eyelid_05_ctrl":
                        #    parent = mc.rename(parent, "RBlinkOffset_PLEASE1")
                        #elif obj == "R_Eyelid_01_ctrl":
                        #    parent = mc.rename(parent, "RBlinkOffset_PLEASE2")
                        offset_grp = mc.group(empty=True, name=f"{obj}_offset")
                        mc.matchTransform(offset_grp, obj)  # Match position and rotation
                        mc.parent(obj, offset_grp)
                        mc.parent(offset_grp, parent[0])
                        mc.setAttr(f"{offset_grp}.scaleY", -1)
                        mc.select(clear=True)
                        print('Did the Thing')
            except Exception as e:
                print(e)

            if rib_group in ['L_Cheek_RIBgrp', 'L_OuterRing_RIBgrp', 'L_LipOuter_RIBgrp', 'L_Lip_RIBgrp', 'R_Cheek_RIBgrp', 'R_OuterRing_RIBgrp', 'R_LipOuter_RIBgrp', 'R_Lip_RIBgrp',]:
                for obj in ctrlz:
                    parent = mc.listRelatives(obj, parent=True)
                    offset_grp = mc.group(empty=True, name=f"{obj}_offset")
                    mc.matchTransform(offset_grp, obj)  # Match position and rotation
                    mc.parent(obj, offset_grp)
                    mc.parent(offset_grp, parent[0])
                    mc.setAttr(f"{offset_grp}.rotateX", -90)
                    mc.select(clear=True)
                    print('Did the Thing')

            
                 

            print("UV Pinning applied to Ribbon and _grps.")

        except Exception as e:
            print(e)

    
    try:
        mc.connectAttr(f'Look_ctrl.Cornea_Vis', f'LeftCornea.visibility')
        mc.connectAttr(f'Look_ctrl.Cornea_Vis', f'RightCornea.visibility')

    except Exception as e:
        print(e)

    for cnt in ['R_Eye_ctrl', 'L_Eye_ctrl']:
        for attr in ['Pupil_Size', 'Iris_Size']:
            try:
                 mc.connectAttr(f'{cnt}.{attr}', f'{cnt}_clone.{attr}')
            except Exception as e:
                print(e)
    '''




    ######################################


    try:
        mc.rename('squashAndStretch_clone|squashStretch_Wire', 'squashStretch_Wire_clone')
        mc.rename('squashAndStretch_clone|squashStretch_CRV', 'squashStretch_CRV_clone')
        mc.rename('squashAndStretch|squashStretch_CRV1', 'squashStretch_CRV')
    except Exception as e:
        print("couldn't rename sqst things:", e)

    try:
        mc.select('*_driver')
        drivers = mc.ls(selection=True)

        for d in drivers:
            try:
                mc.connectAttr(d + '.rotate', d + '1.rotate')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)

    try:
        mc.select('*Mouth_offset_clone')
        drivers = mc.ls(selection=True)

        for d in drivers:
            try:
                mc.disconnectAttr(d[:-6] + '.translate', d + '.translate')
                mc.disconnectAttr(d[:-6] + '.rotate', d + '.rotate')
                mc.disconnectAttr(d[:-6] + '.scale', d + '.scale') 
                mc.connectAttr(d + '.translateX', d[:-6] + '.translateX')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)

    try:
        for s in ['R', 'L']:
            for attr in ['Blink', 'Blink_Height', 'Blink_Influence', 'Eyelid_Follow', s + '_Iris_Scale']:
                mc.connectAttr(f'{s}_eyeCTRL.{attr}', f'{s}_eyeCTRL_clone.{attr}')
    except:
        pass

    try:
        for attr in ['LipInfluence', 'LipSquishValue']:
            mc.connectAttr(f'jaw_ctrl.{attr}', f'jaw_ctrl_clone.{attr}')
    except:
        pass

    try:
        mc.connectAttr('NoseA_CTRL.Nostril_Blend', 'NoseA_CTRL_clone.Nostril_Blend')
    except:
        pass

    try:
        for attr in ['L_Lip_Corner_Pinch', 'L_NLF_Crease', 'Pucker', 'R_Lip_Corner_Pinch', 'R_NLF_Crease']:
            mc.connectAttr(f'Mouth_Global_ctrl.{attr}', f'Mouth_Global_ctrl_clone.{attr}')
    except:
        pass
    #Bobo Test
    try:
        for attr in ['Pupil_Size', 'Iris_Size']:
            mc.connectAttr(f'L_Eye_ctrl.{attr}', f'L_Eye_ctrl_clone.{attr}')
            mc.connectAttr(f'R_Eye_ctrl.{attr}', f'R_Eye_ctrl_clone.{attr}')
    except:
        pass
    

    try:
        mc.select('*_parentConstraint1_clone')
        driver_pc = mc.ls(selection=True)

        for d in driver_pc:
            try:
                mc.connectAttr(d + '.constraintRotate', d[:-24] + '.rotate')
                mc.connectAttr(d + '.constraintTranslate', d[:-24] + '.translate')
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

    try:
        mc.select('*_eyelid_*_Pointer_driver_rotateX')
        driver_rx = mc.ls(selection=True)

        for d in driver_rx:
            try:
                mc.connectAttr(d + '.output', d[:-8] + '.rotateX')
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

    try:
        mc.select('*_eyelid_*_Pointer_driver_aimConstraint1_clone')
        driver_ac = mc.ls(selection = True)

        try:
            for d in driver_ac:
                mc.connectAttr(d + '.constraintRotateY', d[:-21])
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

    try:
        mc.select('*_eyelid_??_OFST')
        el_ofst = mc.ls(selection=True)

        for n in el_ofst:
            try:
                mc.disconnectAttr(n + '_parentConstraint1_clone.constraintRotate', n + '.rotate')
            except Exception as e:
                print('100:', e)
                continue
    except Exception as e:
        print('103:', e)


    #Bobo Fixes
    try:
            mc.connectAttr(f'MasterSnoutlattice_ctrl.Sub_Handle_Vis', f'MasterSnoutlattice_ctrl_clone.Sub_Handle_Vis')
    except:
        pass
    # try:
    #     for attr in ['Elliptical', 'RigScale']:
    #         mc.connectAttr(f'Right_Master_ctrl.{attr}', f'Right_Master_ctrl_clone.{attr}')
    # except:
    #     pass

    # try:
    #     orig = mc.select('*ShapeOrig1')
    #     orig = mc.ls(selection=True)
    #     clean_o, broken_o = [], []
    #     for o in orig:
    #         if '_' not in o:
    #             clean_o.append(o)

    #     for o1 in clean_o:
    #         if mc.objExists(o1[:-1]):
    #             broken_o.append(o1)
            
    #     for o in broken_o:
    #         conn = mc.listConnections(o, d=True)
    #         skc = conn[0]
    #         bs = conn[1]
    #         o_new = o[:-1]
    #         mc.connectAttr(o_new + '.outMesh', bs + '.originalGeometry[0]', f=True)
    #         mc.connectAttr(o_new + '.outMesh', skc + '.originalGeometry[0]', f=True)
    #         mc.connectAttr(o_new + '.worldMesh[0]', bs + '.input[0].inputGeometry', f=True)
    #         mc.delete(o)
    # except Exception as e:
    #     print(e)

    mc.select(cl=True)
            
    mc.hide("HIDE_FACE")
    mc.hide(f_rig)

