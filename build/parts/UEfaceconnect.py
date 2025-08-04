
import maya.cmds as mc
from importlib import reload
import re

import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.build.guide as rGuide
import rjg.libs.transform as rXform
from rjg.build.UEface import UEface
reload(rAttr)
reload(rChain)
reload(rCtrl)
reload (rGuide)
reload(rXform)

class UEfaceconnect(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def build(self, character=None):
        upper_jnt, upper_ctrl, upper_offset = UEface.Simple_joint_and_Control(
            guide='UpperHead_guide',
            overwrite=True,
            overwrite_name='UpperHead',
            orient=True,
            CTRL_Size=9,
            JNT_Size=0.9,
            CTRL_Color=(1, 0.6, 0)
        )
        lower_jnt, lower_ctrl, lower_offset = UEface.Simple_joint_and_Control(
            guide='LowerHead_guide',
            overwrite=True,
            overwrite_name='LowerHead',
            orient=True,
            CTRL_Size=9,
            JNT_Size=0.9,
            CTRL_Color=(1, 0.6, 0)
        )
        mc.parent(lower_jnt, upper_jnt, 'head_M_JNT')
        mc.parent(lower_offset, upper_offset, 'head_M_01_CTRL')

        # Select the set and get its members
        mc.select('UE_Face_Bind')
        all_joints = mc.ls(selection=True)

        # Init groups
        nose_jnts = []
        upper_jnts = []
        lower_jnts = []
        unsorted = []

        # Names to ignore
        ignored_names = ['LowerHead_JNT', 'UpperHead_JNT']

        for jnt in all_joints:
            name = jnt

            # Skip ignored names
            if name in ignored_names:
                continue

            # Remove "Major" joints from set and skip
            if "Major" in name:
                mc.sets(name, remove='UE_Face_Bind')
                continue

            # Sort into categories
            if name == 'Nose_M_NoseRoot_JNT' or 'NLFold' in name:
                nose_jnts.append(name)
            elif any(key in name for key in ['Brow', 'Eye', 'CheekBone']):
                upper_jnts.append(name)
            elif any(key in name for key in ['Mouth', 'Jaw_M_root_JNT', 'Puff']):
                lower_jnts.append(name)
            else:
                unsorted.append(name)

        # Parent to respective head joints
        if mc.objExists('LowerHead_JNT'):
            for jnt in lower_jnts:
                mc.parent(jnt, 'LowerHead_JNT')

        if mc.objExists('UpperHead_JNT'):
            for jnt in upper_jnts:
                mc.parent(jnt, 'UpperHead_JNT')

        if mc.objExists('head_M_JNT'):
            for jnt in nose_jnts:
                mc.parent(jnt, 'head_M_JNT')

        # Print unsorted list
        print("🟡 Unsorted joints:")
        for j in unsorted:
            print(f" - {j}")

        mc.parent('Eye_L_look_offset', 'Eye_R_look_offset', 'UpperHead_M_CTRL')

        look_pos = mc.xform('LookNULL_loc', q=True, os=True, t=True)
        ctrl_name, top_group = UEface.build_basic_control( name='Look_M', shape='circle', size=2.0, color_rgb=(1, 1, 0), position=look_pos, rotation=(90, 0, 0))
        mc.parent('Eye_L_Look_L_CTRL_CNST_GRP', 'Eye_R_Look_R_CTRL_CNST_GRP', ctrl_name)
        mc.group('LookNULL_loc', 'Eye_L_eyelid_look_loc', 'Eye_R_eyelid_look_loc', name='Look_Null')
        mc.parent('Look_Null', 'head_M_01_CTRL')
        mc.hide('Look_Null')
        mc.parent('Look_M_M_CTRL_CNST_GRP', 'RIG')
        mc.parent('Brow_L_NULL', 'Brow_R_NULL', 'UpperHead_M_CTRL')
        mc.hide('Brow_L_NULL', 'Brow_R_NULL')
        mc.parent('Brow_L_Master_L_CTRL_CNST_GRP', 'Brow_R_Master_R_CTRL_CNST_GRP', 'Cheek_R_CheekBone_R_CTRL_CNST_GRP', 'Cheek_L_CheekBone_L_CTRL_CNST_GRP', 'UpperHead_M_CTRL' )
        mc.parentConstraint('Nose_M_NoseRoot_M_CTRL', 'Cheek_L_NLFold_02_Major_jnt', mo=True)
        mc.parentConstraint('Nose_M_NoseRoot_M_CTRL', 'Cheek_R_NLFold_02_Major_jnt', mo=True)
        mc.parentConstraint('Jaw_M_root_M_CTRL', 'Cheek_L_NLFold_05_Major_jnt', mo=True)
        mc.parentConstraint('Jaw_M_root_M_CTRL', 'Cheek_R_NLFold_05_Major_jnt', mo=True)
        mc.parent('Cheek_L_Puff_L_CTRL_CNST_GRP', 'Cheek_R_Puff_R_CTRL_CNST_GRP', 'LowerHead_M_CTRL')
        mc.parent('Nose_Master_Master_CTRL_CNST_GRP', 'head_M_01_CTRL')
        mc.parent('Jaw_M_root_M_CTRL_CNST_GRP', 'LowerHead_M_CTRL')
        mc.parent('TopTeeth_JNT', 'BotTeeth_JNT', 'Tounge_01_JNT', 'head_M_JNT')
        mc.parent('TopTeeth_M_CTRL_CNST_GRP', 'LowerHead_M_CTRL')
        mc.parent('BotTeeth_M_CTRL_CNST_GRP', 'Tounge_01_01_CTRL_CNST_GRP', 'Jaw_M_root_M_CTRL')
        mc.parent('LowerLip_M_M_CTRL_CNST_GRP', 'UpperLip_M_M_CTRL_CNST_GRP', 'Major_Mouth_R_CornerLip_Mouth_CTRL_CNST_GRP', 'Major_Mouth_L_CornerLip_Mouth_CTRL_CNST_GRP', 'LowerHead_M_CTRL')
        mc.parentConstraint('Jaw_M_root_M_CTRL', 'LowerLip_M_M_CTRL_CNST_GRP', mo=True)
        pos = mc.xform('Mouth_M_center', q=True, ws=True, t=True)
        loc = mc.spaceLocator(name='Mouth_NULL_loc')[0]
        # Move it to the desired world position
        mc.xform(loc, worldSpace=True, translation=pos)
        for side in ['L', 'R']:
            mc.pointConstraint('LowerLip_M_M_CTRL_CNST_GRP', f'Major_Mouth_{side}_CornerLip_Mouth_CTRL_CNST_GRP', mo=True)
            mc.pointConstraint(loc, f'Major_Mouth_{side}_CornerLip_Mouth_CTRL_CNST_GRP', mo=True)
            mc.parentConstraint(f'Major_Mouth_{side}_CornerLip_Mouth_CTRL', f'NLFold_{side}_{side}_CTRL_CNST_GRP', mo=True)
            mc.parent(f'Ear_{side}_Root_JNT', 'head_M_JNT')
            mc.parent(f'Ear_{side}_Root_{side}_CTRL_CNST_GRP', 'head_M_01_CTRL')
        mc.parent(loc, 'LowerHead_M_CTRL')

        mc.parent('Eye_L_JNT', 'Eye_R_JNT' ,'UpperHead_JNT' )
        mc.hide('Eye_L_Eyelid_InnerCorner_Major_JNT', 'Eye_L_Eyelid_Lower_Major_JNT', 'Eye_L_Eyelid_OuterCorner_Major_JNT', 'Eye_L_Eyelid_Upper_Major_JNT', 'Eye_R_Eyelid_Upper_Major_JNT', 'Eye_R_Eyelid_OuterCorner_Major_JNT', 'Eye_R_Eyelid_Lower_Major_JNT', 'Eye_R_Eyelid_InnerCorner_Major_JNT', 'Mouth_NULL_loc')
        mc.parentConstraint('LowerHead_M_CTRL', 'Jaw_M_larynx_M_CTRL_CNST_GRP', mo=True)
        mc.parentConstraint('neck_M_02_fk_CTRL', 'Jaw_M_larynx_M_CTRL_CNST_GRP', mo=True)
        mc.parent('Jaw_M_larynx_M_CTRL_CNST_GRP', 'RIG')
        
        
        if character:
            pass



















