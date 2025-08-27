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


class UEbrow(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def build(self):
        prefix = UEface.get_prefix_from_group(self.grp_name)
        
        # Define guide list
        guide_list = mc.listRelatives(self.grp_name, children=True, type='transform', f=False) or []

        # Step 0 - Check required guides
        #check_guides(group, prefix, guide_list)

        # Step 1 - Sort guide categories
        upper_guides = [g for g in guide_list if g.endswith('_Upper')]
        lower_guides = [g for g in guide_list if g.endswith('_Lower')]
        normal_guides = [g for g in guide_list if not any(x in g for x in ['_Upper', '_Lower', '_Major'])]
        major_guides = [f'{prefix}_01_Major', f'{prefix}_02_Major']

        # Step 2 - Build curves and loft
        upper_curve = UEface.build_curve(upper_guides, prefix + '_BrowUpper')
        lower_curve = UEface.build_curve(lower_guides, prefix + '_BrowLower')
        loft_surface = mc.loft(upper_curve, lower_curve, ch=True, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0)[0]
        loft_surface = mc.rename(loft_surface, prefix + '_Brow_ribbon')
        mc.delete(upper_curve, lower_curve)

        # Step 3 - Locator at 03
        center_pos = mc.xform(f'{prefix}_03', q=True, ws=True, t=True)
        null = mc.spaceLocator(name=f'{prefix}_NULL')[0]
        mc.xform(null, ws=True, t=center_pos)

        # Step 4 - Controls + soft joints
        soft_joints = []
        for guide in normal_guides:
            base_name = guide
            jnt, ctrl, offset = UEface.Simple_joint_and_Control(
                guide=guide,
                overwrite=True,
                overwrite_name=base_name,
                orient=False,
                CTRL_Size=0.15,
                JNT_Size=0.4,
                check_side=True
            )

            mc.select(clear=True)
            mc.select(loft_surface)
            mc.select(offset, add=True)
            mc.UVPin()

            mc.select(clear=True)
            pos = mc.xform(guide, q=True, ws=True, t=True,)
            soft_jnt = mc.joint(name=f'{guide}_soft_JNT', p=pos, rad=.6)
            soft_joints.append(soft_jnt)
            UEface.add_to_face_bind_set(soft_jnt)
            mc.pointConstraint(jnt, soft_jnt, mo=True)
            mc.pointConstraint(null, soft_jnt, mo=True)

        # Step 5 - Major controls + major joints
        major_ctrls = []
        for guide in major_guides:
            name = guide
            jnt, ctrl, offset = UEface.Simple_joint_and_Control(
                guide=guide,
                overwrite=True,
                overwrite_name=name,
                orient=True,
                CTRL_Size=.5,
                JNT_Size=0.8,
                check_side=True
            )
            major_ctrls.append((ctrl, offset))

        inner_joint_pos = mc.xform(f'{prefix}_01', q=True, ws=True, t=True)
        outer_joint_pos = mc.xform(f'{prefix}_05', q=True, ws=True, t=True)
        mc.select(clear=True)
        inner_major = mc.joint(name=f'{prefix}_Inner_major_JNT', p=inner_joint_pos)
        mc.select(clear=True)
        outer_major = mc.joint(name=f'{prefix}_Outer_major_JNT', p=outer_joint_pos)

        # Step 6 - Skin loft to 4 major joints
        skin_joints = [f'{prefix}_01_Major_JNT', f'{prefix}_02_Major_JNT', inner_major, outer_major]
        mc.select([loft_surface] + skin_joints)
        mc.skinCluster(tsb=True)

        # Step 7 - Inner/Outer controls
        io_ctrls = []
        for i, name in enumerate(['Inner', 'Outer']):
            guide = major_guides[i]
            pos = mc.xform(guide, q=True, ws=True, t=True)
            ctrl, offset = UEface.build_basic_control(
                name=f'{prefix}_{name}',
                position=pos,
                size=.75,
                color_rgb=(1, 0.5, 0)
            )
            io_ctrls.append((ctrl, offset))

            # Parent major ctrl's offset under this new control
            mc.parent(major_ctrls[i][1], ctrl)

            # Parent constrain to major joint
            jnt_target = inner_major if name == 'Inner' else outer_major
            mc.parentConstraint(ctrl, jnt_target, mo=True)

        # Step 8 - Master control
        all_joints = [mc.xform(j, q=True, ws=True, t=True) for j in [inner_major, outer_major] + [j for j, _ in major_ctrls]]
        avg_pos = [sum(p[i] for p in all_joints) / len(all_joints) for i in range(3)]
        master_ctrl, master_offset = UEface.build_basic_control(
            name=f'{prefix}_Master',
            position=avg_pos,
            size=1,

        )

        # Parent offset groups under master
        for _, offset in io_ctrls:
            mc.parent(offset, master_ctrl)

        side = prefix.split('_')[-1]  # "L"
        mc.select(clear=True)
        mc.group(f'{prefix}_Brow_ribbon', f'{prefix}_01_{side}_CTRL_CNST_GRP', f'{prefix}_02_{side}_CTRL_CNST_GRP', f'{prefix}_03_{side}_CTRL_CNST_GRP', f'{prefix}_04_{side}_CTRL_CNST_GRP', f'{prefix}_05_{side}_CTRL_CNST_GRP', f'{prefix}_01_Major_JNT', f'{prefix}_02_Major_JNT', f'{prefix}_Inner_major_JNT', f'{prefix}_Outer_major_JNT',  name=f'{prefix}_extras_offset_grp')
        mc.parent(f'{prefix}_extras_offset_grp', "RIG")
        mc.hide(f'{prefix}_Inner_major_JNT', f'{prefix}_01_Major_JNT', f'{prefix}_02_Major_JNT', f'{prefix}_Outer_major_JNT', f'{prefix}_Brow_ribbon')
#        for object in [f'{prefix}_Brow_ribbon', f'{prefix}_01_{side}_CTRL_CNST_GRP', f'{prefix}_02_{side}_CTRL_CNST_GRP', f'{prefix}_03_{side}_CTRL_CNST_GRP', f'{prefix}_04_{side}_CTRL_CNST_GRP', f'{prefix}_05_{side}_CTRL_CNST_GRP', f'{prefix}_01_Major_JNT', f'{prefix}_02_Major_JNT', f'{prefix}_Inner_major_JNT', f'{prefix}_Outer_major_JNT']:
#            mc.parent(object, f'{prefix}_extras_offset_grp')
