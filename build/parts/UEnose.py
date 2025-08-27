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


class UEnose(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

 
    def build(self):
        suffix = UEface.get_prefix_from_group(self.grp_name)
    
        # Guides to check (base names)
        guide_basenames = [
            'M_Tip', 'L_Nostril', 'L_Nostril_Outer', 'M_NoseBridge',
            'M_Nostril_Inner', 'L_UpperCorner', 'R_Nostril',
            'R_Nostril_Outer', 'R_UpperCorner', 'M_NoseRoot'
        ]
        full_guide_names = [f'{suffix}_{name}' for name in guide_basenames]
        
        print(full_guide_names)

        #check_guides(guide_group, full_guide_names)

        # === Step 2: Build Simple Joint & Control ===
        for base in guide_basenames:
            if base == 'M_NoseRoot':
                continue  # We'll build this separately
            UEface.Simple_joint_and_Control(
                guide=f'{suffix}_{base}',
                suffix=suffix,
                check_side=True,
                CTRL_Size=.5,
                JNT_Size=0.5
            )

        # === Step 3: Build Nose Master Control at M_NoseBridge ===
        bridge_guide = f'{suffix}_M_NoseBridge'
        master_pos = mc.xform(bridge_guide, q=True, ws=True, t=True)
        Nose_Master_CTRL, Nose_Master_GRP = UEface.build_basic_control(
            name=f'{suffix}_Master',
            size=1.5,
            color_rgb=(1, 0.6, 0),  # Orangey Yellow
            position=master_pos,
            rotation=(0, 0, 0)
        )

        # === Step 4: Build Nose Root Control/Joint ===
        UEface.Simple_joint_and_Control(
            guide=f'{suffix}_M_NoseRoot',
            suffix=suffix,
            check_side=False,
            CTRL_Size=1.5,
            CTRL_Color=(1, 0.6, 0),
            JNT_Size=0.5
        )

        # === Step 5: Parenting Nesting ===
        def parent_offset_under_ctrl(child_base, parent_base):
            child_grp = f"{suffix}_{child_base}_GRP"
            parent_ctrl = f"{suffix}_{parent_base}_CTRL"
            if mc.objExists(child_grp) and mc.objExists(parent_ctrl):
                mc.parent(child_grp, parent_ctrl)

        # Parent nostril outers
        #parent_offset_under_ctrl('L_Nostril_Outer', 'L_Nostril')
        #parent_offset_under_ctrl('R_Nostril_Outer', 'R_Nostril')

        # === Step 6: Parent nostril controls under Nose Root ===
        nostril_names = ['L_Nostril', 'R_Nostril', 'M_Nostril_Inner', 'M_Tip']
        for name in nostril_names:
            grp = f"{suffix}_{name}_GRP"
            root_ctrl = f"{suffix}_M_NoseRoot_CTRL"
            if mc.objExists(grp) and mc.objExists(root_ctrl):
                mc.parent(grp, root_ctrl)

        # === Step 7: Parent upper parts under Nose Master ===
        #upper_parts = ['M_NoseRoot', 'R_UpperCorner', 'L_UpperCorner', 'M_NoseBridge']
        #for name in upper_parts:
        #    grp = f"{suffix}_{name}_GRP"
        #    if mc.objExists(grp):
        #        mc.parent(grp, Nose_Master_CTRL)
        mc.parent(f'{suffix}_L_Nostril_Outer_L_CTRL_CNST_GRP', f'{suffix}_L_Nostril_L_CTRL')
        mc.parent(f'{suffix}_R_Nostril_Outer_R_CTRL_CNST_GRP', f'{suffix}_R_Nostril_R_CTRL')
        for guide in ['L_Nostril', 'R_Nostril', 'M_Nostril_Inner', 'M_Tip']:
            side = guide.split('_')[0] if '_' in guide else 'Unknown'
            mc.parent(f'{suffix}_{guide}_{side}_CTRL_CNST_GRP', f'{suffix}_M_NoseRoot_M_CTRL')

        for guide in ['M_NoseRoot', 'R_UpperCorner', 'L_UpperCorner', 'M_NoseBridge']:
            side = guide.split('_')[0] if '_' in guide else 'Unknown'
            mc.parent(f'{suffix}_{guide}_{side}_CTRL_CNST_GRP', f'{suffix}_Master_Master_CTRL')

        for jnt in ['Nose_L_Nostril_JNT', 'Nose_R_Nostril_JNT', 'Nose_M_Nostril_Inner_JNT', 'Nose_R_Nostril_Outer_JNT', 'Nose_R_UpperCorner_JNT', 'Nose_L_UpperCorner_JNT', 'Nose_L_Nostril_Outer_JNT', 'Nose_M_Tip_JNT', 'Nose_M_NoseBridge_JNT']:
            mc.parent(jnt, 'Nose_M_NoseRoot_JNT')
        print(f"✅ Built nose module for group: {self.grp_name} (suffix: {suffix})")

