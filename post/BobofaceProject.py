import maya.cmds as mc
import maya.mel as mel

from importlib import reload
import rjg.libs.file as rFile
import rjg.libs.control.ctrl as rCtrl
reload(rFile)
reload(rCtrl)

def disconnect_clone_transforms(group_list):
    for group in group_list:
        clone = f"{group}_clone"
        if not mc.objExists(clone):
            print(f"Clone '{clone}' does not exist. Skipping.")
            continue

        for attr in ['translate', 'rotate', 'scale']:
            source_attr = f"{group}.{attr}"
            dest_attr = f"{clone}.{attr}"

            if mc.isConnected(source_attr, dest_attr):
                try:
                    mc.disconnectAttr(source_attr, dest_attr)
                    print(f"Disconnected {source_attr} -> {dest_attr}")
                except Exception as e:
                    print(f"Failed to disconnect {source_attr} -> {dest_attr}: {e}")
            else:
                print(f"No connection to disconnect: {source_attr} -> {dest_attr}")


def setup_proximity_pins(offset_groups, geo):
    shape_name = geo  # Can be changed later

    for group in offset_groups:
        try:
            if not mc.objExists(group):
                print(f"Object '{group}' does not exist. Skipping.")
                continue

            # Create proximityPin node
            prox_node = mc.createNode('proximityPin', name=f'{group}_proximityPin')
            mc.setAttr(f"{prox_node}.coordMode", 1)
            mc.setAttr(f"{prox_node}.normalAxis", 1)
            mc.setAttr(f"{prox_node}.tangentAxis", 0)

            # Connect proximityPin.outputMatrix[0] to group's offsetParentMatrix
            mc.connectAttr(f'{prox_node}.outputMatrix[0]', f'{group}.offsetParentMatrix', force=True)

            # Connect FaceAtOriginOrig.outMesh to proximityPin.originalGeometry
            mc.connectAttr(f'{shape_name}ShapeOrig.outMesh', f'{prox_node}.originalGeometry', force=True)

            # Connect FaceAtOriginShape.worldMesh[0] to proximityPin.deformedGeometry
            mc.connectAttr(f'{shape_name}Shape.worldMesh[0]', f'{prox_node}.deformedGeometry', force=True)

            # Get worldMatrix of the group
            world_matrix = mc.getAttr(f'{group}.worldMatrix[0]')

            # Set inputMatrix[0] to the group's worldMatrix
            mc.setAttr(f'{prox_node}.inputMatrix[0]', *world_matrix, type='matrix')

            # Now zero out translation and rotation, and set scale to 1 on the offset group itself
            mc.setAttr(f"{group}.translate", 0, 0, 0)
            mc.setAttr(f"{group}.rotate", 0, 0, 0)
            mc.setAttr(f"{group}.scale", 1, 1, 1)

            print(f"Connected proximityPin and zeroed transforms for: {group}")

        except Exception as e:
            print(f"Error processing {group}: {e}")


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

    ####### Cutom Channel Connections #######
    try:
        for attr in ['Pupil_Size', 'Iris_Size', 'Blink']:
            mc.connectAttr(f'L_Aim_ctrl.{attr}', f'L_Aim_ctrl_clone.{attr}')
            mc.connectAttr(f'R_Aim_ctrl.{attr}', f'R_Aim_ctrl_clone.{attr}')
    except Exception as e:
        print(e)  

    ##### Sub Controls ###


    offset_groups = ['L_subLowerLip_02_grp', 'L_subEye_01_grp', 'L_subEye_07_grp', 'R_subUpperLip_09_grp', 'L_subLowerLip_03_grp', 'L_subEye_14_grp', 'R_subEye_09_grp', 'R_subEye_10_grp', 'L_subEye_05_grp', 'L_subUpperLip_06_grp', 'L_subEye_11_grp', 'R_subLowerLip_05_grp', 'L_subLowerLip_04_grp', 'R_subEye_02_grp', 'L_subEye_03_grp', 'R_subUpperLip_07_grp', 'L_subUpperLip_04_grp', 'L_subUpperLip_05_grp', 'R_subUpperLip_10_grp', 'R_subEye_03_grp', 'L_subEye_10_grp', 'R_subLowerLip_03_grp', 'R_subEye_04_grp', 'L_subEye_13_grp', 'L_subUpperLip_10_grp', 'R_subUpperLip_08_grp', 'R_subLowerLip_02_grp', 'R_subEye_13_grp', 'L_subLowerLip_05_grp', 'R_subLowerLip_08_grp', 'R_subEye_16_grp', 'L_subUpperLip_07_grp', 'R_subLowerLip_04_grp', 'L_subUpperLip_03_grp', 'M_subUpperLip_01_grp', 'L_subEye_02_grp', 'L_subEye_16_grp', 'R_subUpperLip_04_grp', 'L_subEye_04_grp', 'R_subUpperLip_11_grp', 'L_subLowerLip_06_grp', 'R_subEye_01_grp', 'L_subEye_08_grp', 'L_subLowerLip_07_grp', 'R_subUpperLip_05_grp', 'M_subLowerLip_01_grp', 'R_subEye_15_grp', 'R_subEye_06_grp', 'R_subLowerLip_06_grp', 'L_subEye_12_grp', 'L_subLowerLip_09_grp', 'R_subEye_11_grp', 'L_subUpperLip_02_grp', 'R_subUpperLip_02_grp', 'L_subUpperLip_09_grp', 'R_subEye_05_grp', 'R_subEye_08_grp', 'R_subEye_12_grp', 'L_subEye_15_grp', 'R_subLowerLip_07_grp', 'R_subUpperLip_06_grp', 'L_subUpperLip_08_grp', 'R_subLowerLip_09_grp', 'L_subLowerLip_08_grp', 'L_subEye_06_grp', 'R_subEye_14_grp', 'R_subEye_07_grp', 'L_subUpperLip_11_grp', 'L_subEye_09_grp', 'R_subUpperLip_03_grp']



    #offset_groups = ['L_subLowerLip_02_grp', 'L_subEye_01_grp', 'L_subEye_07_grp', 'R_subUpperLip_09_grp', 'L_subLowerLip_03_grp', 'L_subEye_14_grp', 'R_subEye_09_grp', 'R_subEye_10_grp', 'L_subEye_05_grp', 'L_subUpperLip_06_grp', 'L_subEye_11_grp', 'R_subLowerLip_05_grp', 'L_subLowerLip_04_grp', 'R_subEye_02_grp', 'L_subEye_03_grp', 'R_subUpperLip_07_grp', 'L_subUpperLip_04_grp', 'L_subUpperLip_05_grp', 'R_subUpperLip_10_grp', 'R_subEye_03_grp', 'L_subEye_10_grp', 'R_subLowerLip_03_grp', 'R_subEye_04_grp', 'L_subEye_13_grp', 'L_subUpperLip_10_grp', 'R_subUpperLip_08_grp', 'R_subLowerLip_02_grp', 'R_subEye_13_grp', 'L_subLowerLip_05_grp', 'R_subLowerLip_08_grp', 'R_subEye_16_grp', 'L_subUpperLip_07_grp', 'R_subLowerLip_04_grp', 'L_subUpperLip_03_grp', 'M_subUpperLip_01_grp', 'L_subEye_02_grp', 'L_subEye_16_grp', 'R_subUpperLip_04_grp', 'L_subEye_04_grp', 'R_subUpperLip_11_grp', 'L_subLowerLip_06_grp', 'R_subEye_01_grp', 'L_subEye_08_grp', 'L_subLowerLip_07_grp', 'R_subUpperLip_05_grp', 'M_subLowerLip_01_grp', 'R_subEye_15_grp', 'R_subEye_06_grp', 'R_subLowerLip_06_grp', 'L_subEye_12_grp', 'L_subLowerLip_09_grp', 'R_subEye_11_grp', 'L_subUpperLip_02_grp', 'R_subUpperLip_02_grp', 'L_subUpperLip_09_grp', 'R_subEye_05_grp', 'R_subEye_08_grp', 'R_subEye_12_grp', 'L_subEye_15_grp', 'R_subLowerLip_07_grp', 'R_subUpperLip_06_grp', 'L_subUpperLip_08_grp', 'R_subLowerLip_09_grp', 'L_subLowerLip_08_grp', 'L_subEye_06_grp', 'R_subEye_14_grp', 'R_subEye_07_grp', 'L_subUpperLip_11_grp', 'L_subEye_09_grp', 'R_subUpperLip_03_grp']
    disconnect_clone_transforms(offset_groups)
    
    left_eye = ['L_subEye_10_grp', 'L_subEye_03_grp', 'L_subEye_11_grp', 'L_subEye_01_grp', 'L_subEye_09_grp', 'L_subEye_15_grp', 'L_subEye_04_grp', 'L_subEye_06_grp', 'L_subEye_16_grp', 'L_subEye_07_grp', 'L_subEye_13_grp', 'L_subEye_14_grp', 'L_subEye_08_grp', 'L_subEye_12_grp', 'L_subEye_05_grp', 'L_subEye_02_grp']
    right_eye = ['R_subEye_15_grp', 'R_subEye_05_grp', 'R_subEye_07_grp', 'R_subEye_13_grp', 'R_subEye_02_grp', 'R_subEye_14_grp', 'R_subEye_12_grp', 'R_subEye_09_grp', 'R_subEye_01_grp', 'R_subEye_06_grp', 'R_subEye_16_grp', 'R_subEye_11_grp', 'R_subEye_08_grp', 'R_subEye_04_grp', 'R_subEye_03_grp', 'R_subEye_10_grp']
    Upper_mouth = ['R_subUpperLip_10_grp', 'R_subUpperLip_11_grp', 'R_subUpperLip_09_grp', 'R_subUpperLip_08_grp', 'R_subUpperLip_07_grp', 'R_subUpperLip_05_grp', 'R_subUpperLip_06_grp', 'R_subUpperLip_04_grp', 'L_subUpperLip_03_grp', 'R_subUpperLip_03_grp', 'L_subUpperLip_04_grp', 'M_subUpperLip_01_grp', 'R_subUpperLip_02_grp', 'L_subUpperLip_02_grp', 'L_subUpperLip_05_grp', 'L_subUpperLip_06_grp', 'L_subUpperLip_07_grp', 'L_subUpperLip_08_grp', 'L_subUpperLip_09_grp', 'L_subUpperLip_10_grp', 'L_subUpperLip_11_grp']
    Lower_Lip = [
    'L_subLowerLip_08_grp', 'R_subLowerLip_06_grp', 'L_subLowerLip_02_grp',
    'R_subLowerLip_05_grp', 'R_subLowerLip_02_grp', 'R_subLowerLip_08_grp',
    'L_subLowerLip_06_grp', 'R_subLowerLip_07_grp', 'R_subLowerLip_04_grp',
    'L_subLowerLip_03_grp', 'M_subLowerLip_01_grp', 'R_subLowerLip_09_grp',
    'L_subLowerLip_04_grp', 'R_subLowerLip_03_grp', 'L_subLowerLip_05_grp',
    'L_subLowerLip_09_grp', 'L_subLowerLip_07_grp'
]
    eye_sub = ['L_SubEye02_grp', 'L_SubEye03_grp', 'L_SubEye04_grp', 'L_SubEye05_grp', 'L_SubEye06_grp', 'L_SubEye07_grp', 'L_SubEye08_grp', 'L_SubEye01_grp', 'R_SubEye02_grp', 'R_SubEye01_grp', 'R_SubEye08_grp', 'R_SubEye07_grp', 'R_SubEye06_grp', 'R_SubEye05_grp', 'R_SubEye04_grp', 'R_SubEye03_grp']

    setup_proximity_pins(eye_sub, 'ProximityHelper_clone')
    #setup_proximity_pins(right_eye, 'ProximityHelper_clone')
    setup_proximity_pins(Upper_mouth, 'ProximityHelper3_clone')
    setup_proximity_pins(Lower_Lip, 'ProximityHelper2_clone')
    #setup_proximity_pins(offset_groups)
    #disconnect_clone_transforms(offset_groups)
    #mc.parent('SubControls', 'RIG')

    ###### Jaw ####

    try:
        # Create remapValue node
        remap_node = mc.createNode('remapValue', name='jawRotateToTranslate_remap')

        # Set input/output max values
        mc.setAttr(f'{remap_node}.inputMax', 180)
        mc.setAttr(f'{remap_node}.outputMax', 26)

        # Connect input and output
        mc.connectAttr('L_Jaw_Base_jnt_ctrl.rotateX', f'{remap_node}.inputValue', force=True)
        mc.connectAttr(f'{remap_node}.outValue', 'L_Jaw_Translate_Offset.translateZ', force=True)

        print(f'Remap node created: {remap_node}') 
    except Exception as e:
        print(e)


    #####################################3 
    '''
    Bobo Custom Connection needs
    xxxxxxx  Ribbons
    Influence Constraint Set up
    Cornea Vis

    '''
    #Ribbon FIX
    # Define a dictionary where each rib group has a fixed number of control pins

    ######################################
    try:
        # Full list of objects
        grp_list = [
        'ToungeRight_ribbon_point6_DEF_grp', 'ToungeRight_ribbon_point3_DEF_grp',
        'ToungeLeft_ribbon_point5_DEF_grp', 'ToungeLeft_ribbon_point3_DEF_grp',
        'ToungeRight_ribbon_point7_DEF_grp', 'ToungeRight_ribbon_point8_DEF_grp',
        'ToungeRight_ribbon_point1_DEF_grp', 'ToungeRight_ribbon_point4_DEF_grp',
        'ToungeLeft_ribbon_point8_DEF_grp', 'ToungeLeft_ribbon_point7_DEF_grp',
        'ToungeLeft_ribbon_point10_DEF_grp', 'ToungeLeft_ribbon_point6_DEF_grp',
        'ToungeRight_ribbon_point5_DEF_grp', 'ToungeLeft_ribbon_point4_DEF_grp'
        ]

        # Separate them based on name
        right_target = 'ToungeRight_ribbon'
        left_target = 'ToungeLeft_ribbon'

        right_grp = [grp for grp in grp_list if 'ToungeRight' in grp]
        left_grp = [grp for grp in grp_list if 'ToungeLeft' in grp]

        # Pin to the right ribbon
        for grp in right_grp:
            if mc.objExists(grp) and mc.objExists(right_target):
                mc.select(clear=True)
                mc.select(right_target, grp)
                mc.UVPin()
            else:
                mc.warning(f"Missing object: {grp} or {right_target}")
        # Pin to the left ribbon
        for grp in left_grp:
            if mc.objExists(grp) and mc.objExists(left_target):
                mc.select(clear=True)
                mc.select(left_target, grp)
                mc.UVPin()
            else:
                mc.warning(f"Missing object: {grp} or {left_target}")
    except Exception as e:
                print(e)
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
        for attr in ['Pupil_Size', 'Iris_Size', 'Blink']:
            mc.connectAttr(f'L_Aim_ctrl.{attr}', f'L_Eye_ctrl_clone.{attr}')
            mc.connectAttr(f'R_Aim_ctrl.{attr}', f'R_Eye_ctrl_clone.{attr}')
    except:
        pass
    '''
    try:
        parent_list = []
        for control in ['R_Eye_upper_ctrl', 'R_Eye_outer_ctrl', 'R_Eye_lower_ctrl', 'R_Eye_inner_ctrl', 'R_EyeRing_Inner__ctrl', 'R_EyeRing_Lower__ctrl', 'R_EyeRing_Outer__ctrl', 'R_EyeRing_Upper__ctrl', 'L_Eye_inner_ctrl', 'L_EyeRing_Inner__ctrl', 'L_Eye_upper_ctrl', 'L_EyeRing_Upper__ctrl', 'L_Eye_outer_ctrl', 'L_EyeRing_Outer__ctrl', 'L_EyeRing_Lower__ctrl', 'L_Eye_lower_ctrl', 'L_Brow1_ctrl', 'L_Brow2_ctrl', 'L_Brow3_ctrl', 'R_Brow1_ctrl', 'R_Brow2_ctrl', 'R_Brow3_ctrl', 'R_Jaw_Null9_ctrl', 'R_Snout_04_jnt_ctrl', 'R_Lip_04_jnt_ctrl', 'L_Lip_04_jnt_ctrl', 'L_Jaw_Null9_ctrl', 'L_Snout_04_jnt_ctrl']:
            parent = mc.listRelatives(control, parent=True)
            if parent:
                parent_list.append(parent[0])
            else:
                parent_list.append(None)  # No parent (probably a top node)
        mc.select(clear=True)
        mc.select("Bobo_UBM")
        mc.select(parent_list, add=True)

        # Run the UVPin command
        mc.UVPin()
        for obj in parent_list:
            mc.setAttr(f"{obj}.translate", 0, 0, 0, type="double3")
            mc.setAttr(f"{obj}.rotate", 0, 0, 0, type="double3")
    except Exception as e:
        print(e)
    '''




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

