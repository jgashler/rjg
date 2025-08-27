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


class UEcheek(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def build(self):
        prefix = UEface.get_prefix_from_group(self.grp_name)

        required_guides = [
            f'{prefix}_NLFold_0{i}_inner' for i in [5,4,3,2,1]
        ] + [
            f'{prefix}_NLFold_0{i}_outer' for i in [1,2,3,4,5]
        ] + [
            f'{prefix}_Puff',
            f'{prefix}_CheekBone'
        ]
        #check_guides(group, prefix, required_guides)

        inner_guides = [f'{prefix}_NLFold_0{i}_inner' for i in [5,4,3,2,1]]
        outer_guides = [f'{prefix}_NLFold_0{i}_outer' for i in [1,2,3,4,5]]

        # Step 1 - Build curves
        inner_curve = UEface.build_curve(inner_guides, prefix + '_NLFold_inner')
        outer_curve = UEface.build_curve(outer_guides, prefix + '_NLFold_outer')

        # Step 2 - Loft surface
        ribbon_surface = mc.loft(inner_curve, outer_curve, ch=False, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0,)[0]
        ribbon_surface = mc.rename(ribbon_surface, prefix + '_NLFold_ribbon')
        mc.delete(inner_curve, outer_curve)

        # Step 3 - Build center controls
        mid_controls = []
        for i in range(1, 6):
            inner = f'{prefix}_NLFold_0{i}_inner'
            outer = f'{prefix}_NLFold_0{i}_outer'

            pos_inner = mc.xform(inner, q=True, ws=True, t=True)
            pos_outer = mc.xform(outer, q=True, ws=True, t=True)
            center = [(a + b) / 2.0 for a, b in zip(pos_inner, pos_outer)]

            ctrl_base = f'{prefix}_NLFold_0{i}'
            jnt, ctrl, offset = UEface.Simple_joint_and_Control(
                guide=inner,
                overwrite=True,
                overwrite_name=ctrl_base,
                orient=True,
                CTRL_Size=0.2,
                JNT_Size=0.5,
                check_side=True,
            )
            mc.xform(offset, ws=True, t=center)
            mid_controls.append((jnt, ctrl, offset))

            # UVPin
            mc.select(clear=True)
            mc.select(ribbon_surface)
            mc.select(offset, add=True)
            mc.UVPin()

        # Step 4 - Add major joints
        major_joints = []
        for i in [2, 4, 5]:
            mc.select(clear=True)
            inner = f'{prefix}_NLFold_0{i}_inner'
            outer = f'{prefix}_NLFold_0{i}_outer'

            # Calculate center position
            pos_inner = mc.xform(inner, q=True, ws=True, t=True)
            pos_outer = mc.xform(outer, q=True, ws=True, t=True)
            center_pos = [(a + b) / 2.0 for a, b in zip(pos_inner, pos_outer)]

            # Use rotation from inner
            rot_inner = mc.xform(inner, q=True, ws=True, ro=True)

            jnt_name = f'{prefix}_NLFold_0{i}_Major_jnt'
            jnt = mc.joint(name=jnt_name, p=center_pos)
            mc.xform(jnt, ws=True, ro=rot_inner)

            major_joints.append(jnt)
        # Step 5 - Skin ribbon
        mc.select([ribbon_surface] + major_joints)
        mc.skinCluster(tsb=True)
        

        pos = mc.xform(f'{prefix}_NLFold_04', q=True, ws=True, t=True)
        rot = mc.xform(f'{prefix}_NLFold_04', q=True, ws=True, ro=True)

        side = prefix.split('_')[-1]  # "L"
        ctrl_name, top_group = UEface.build_basic_control( name=f'NLFold_{side}', shape='circle', size=.5, position=pos, rotation=rot)
        mc.parentConstraint(ctrl_name, f'{prefix}_NLFold_04_Major_jnt', mo=True)

        # Step 6 - Cheek Puff & Bone
        for name in ['Puff', 'CheekBone']:
            guide = f'{prefix}_{name}'
            UEface.Simple_joint_and_Control(
                guide=guide,
                overwrite=True,
                overwrite_name=f'{prefix}_{name}',
                CTRL_Size=0.7,
                check_side=True,
                JNT_Size=0.4,
            )
        side = prefix.split('_')[-1]  # "L"
        mc.group(top_group, f'{prefix}_NLFold_ribbon', f'{prefix}_NLFold_01_{side}_CTRL_CNST_GRP', f'{prefix}_NLFold_02_{side}_CTRL_CNST_GRP', f'{prefix}_NLFold_03_{side}_CTRL_CNST_GRP', f'{prefix}_NLFold_04_{side}_CTRL_CNST_GRP', f'{prefix}_NLFold_05_{side}_CTRL_CNST_GRP', f'{prefix}_NLFold_02_Major_jnt', f'{prefix}_NLFold_04_Major_jnt', f'{prefix}_NLFold_05_Major_jnt', name=f'{prefix}_extra_offsets' )
        mc.parent(f'{prefix}_extra_offsets', 'RIG')
        mc.hide(f'{prefix}_NLFold_ribbon', f'{prefix}_NLFold_02_Major_jnt', f'{prefix}_NLFold_04_Major_jnt', f'{prefix}_NLFold_05_Major_jnt')