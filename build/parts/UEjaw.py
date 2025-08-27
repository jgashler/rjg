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


class UEjaw(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def build(self):
        prefix = UEface.get_prefix_from_group(self.grp_name)
    
        required = [f'{prefix}_ee', f'{prefix}_root', f'{prefix}_larynx']
        #check_guides(group, prefix, required)

        # Step 1: Build controls
        ee_jnt, ee_ctrl, ee_offset = UEface.Simple_joint_and_Control(
            guide=f'{prefix}_ee',
            overwrite=True,
            overwrite_name=f'{prefix}_ee',
            orient=True,
            CTRL_Size=.5,
            JNT_Size=0.5,
            CTRL_Color=(1, 0.6, 0)
        )

        larynx_jnt, larynx_ctrl, larynx_offset = UEface.Simple_joint_and_Control(
            guide=f'{prefix}_larynx',
            overwrite=True,
            overwrite_name=f'{prefix}_larynx',
            orient=True,
            CTRL_Size=.5,
            JNT_Size=0.5,
            CTRL_Color=(1, 0.6, 0)
        )

        root_jnt, root_ctrl, root_offset = UEface.Simple_joint_and_Control(
            guide=f'{prefix}_root',
            overwrite=True,
            overwrite_name=f'{prefix}_root',
            orient=True,
            CTRL_Size=9,
            JNT_Size=0.9,
            CTRL_Color=(1, 0.6, 0)
        )

        # Step 2: Chain root -> ee
        UEface.chain_parts([f'{prefix}_root', f'{prefix}_ee'], joints=True, controls=True)

        # Step 3: Create trans offset group
        trans_offset = mc.group(em=True, name=f'{prefix}_trans_offset')
        root_guide_pos = mc.xform(f'{prefix}_root', q=True, ws=True, t=True)
        root_guide_rot = mc.xform(f'{prefix}_root', q=True, ws=True, ro=True)
        mc.xform(trans_offset, ws=True, t=root_guide_pos)
        mc.xform(trans_offset, ws=True, ro=root_guide_rot)

        mc.parent(trans_offset, root_offset)
        mc.parent(root_ctrl, trans_offset)

        # Step 4: MultiplyDivide setup
        mult_node = mc.createNode('multiplyDivide', name=f'{prefix}_TransX_MultDiv')
        mc.setAttr(f'{mult_node}.input2X', 0.007)

        mc.connectAttr(f'{root_ctrl}.rotateX', f'{mult_node}.input1X')
        mc.connectAttr(f'{mult_node}.outputX', f'{trans_offset}.translateZ')
        mc.parent('Jaw_M_ee_M_CTRL_CNST_GRP', 'Jaw_M_root_M_CTRL')
        mc.parent('Jaw_M_larynx_JNT', 'Jaw_M_root_JNT')
        
        mult_node2 = mc.createNode('multiplyDivide', name=f'{prefix}_TransX_MultDiv')
        mc.setAttr(f'{mult_node2}.input2X', -0.05)
        mc.connectAttr(f'{root_ctrl}.rotateX', f'{mult_node2}.input1X')
        mc.connectAttr(f'{mult_node2}.outputX', f'Jaw_M_larynx_M_CTRL_OFF_GRP.translateY')

