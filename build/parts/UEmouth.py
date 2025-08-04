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

class UEmouth(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Brow', grp_name=grp_name, ctrl_scale=ctrl_scale)

    def get_ordered_lip_guides(self, prefix, guides, guide_base, has_mid=True):
        """
        Builds an ordered list of lip guide names for a given region (UpperLip, LowerLip, etc.)

        Parameters:
        - prefix: str, e.g. 'Mouth_'
        - guides: list[str], e.g. ['R_UpperLip_01', ..., 'L_CornerLip']
        - guide_base: str, e.g. 'UpperLip', 'LowerOuter'
        - has_mid: bool, whether to include a center guide like 'M_UpperLip_01'

        Returns:
        - list[str]: ordered full names like ['Mouth_R_CornerLip', ..., 'Mouth_L_CornerLip']
        """
        use_outer_corners = 'Outer' in guide_base
        right_corner = f"{prefix}R_CornerOuter" if use_outer_corners else f"{prefix}R_CornerLip"
        left_corner = f"{prefix}L_CornerOuter" if use_outer_corners else f"{prefix}L_CornerLip"

        ordered = []
        # Right corner
        if right_corner in guides:
            ordered.append(right_corner)

        # Right side (sorted descending)
        right_side = sorted(
            [g for g in guides if g.startswith(f"{prefix}R_") and guide_base in g],
            reverse=True
        )
        ordered.extend(right_side)

        # Mid
        if has_mid:
            mid_guide = f"{prefix}M_{guide_base}_01"
            if mid_guide in guides:
                ordered.append(mid_guide)

        # Left side (sorted ascending)
        left_side = sorted(
            [g for g in guides if g.startswith(f"{prefix}L_") and guide_base in g]
        )
        ordered.extend(left_side)

        # Left corner
        if left_corner in guides:
            ordered.append(left_corner)

        # Strip the prefix from the list
        striped_list = [loc.removeprefix(prefix) for loc in ordered]
        return ordered
    
    def build(self):
        prefix = UEface.get_prefix_from_group(self.grp_name)
        guide_list = mc.listRelatives(self.grp_name, children=True, type='transform', f=False) or []
        #check_guides(group, prefix, guide_list)

        # Step 2 - Organize guides by region and side
        def collect_guides(region):
            pattern = re.compile(r'([LRM])_' + region + r'_(\d{2})')
            found = {'L': [], 'M': [], 'R': []}
            for guide in guide_list:
                match = pattern.match(guide)
                if match:
                    side, num = match.groups()
                    found[side].append((int(num), guide))
            return (
                [g for _, g in sorted(found['R'], reverse=True)] +
                [g for _, g in sorted(found['M'])] +
                [g for _, g in sorted(found['L'])]
            )

        guides = mc.listRelatives(f'{prefix}_guides', children=True, type='transform')

        upper_lip = self.get_ordered_lip_guides(f'{prefix}_', guides, 'UpperLip', has_mid=True)
        lower_lip = self.get_ordered_lip_guides(f'{prefix}_', guides, 'LowerLip', has_mid=True)
        #upper_outer = self.get_ordered_lip_guides(f'{prefix}_', guides, 'UpperOuter', has_mid=False)
        #lower_outer = self.get_ordered_lip_guides(f'{prefix}_', guides, 'LowerOuter', has_mid=False)
        print(upper_lip)
        # Step 3 - Build curves
        upper_lip_curve = UEface.build_curve(upper_lip, f'{prefix}_UpperLip')
        lower_lip_curve = UEface.build_curve(lower_lip, f'{prefix}_LowerLip')
        #upper_outer_curve = UEface.build_curve(upper_outer, f'{prefix}_UpperOuter')
        #lower_outer_curve = UEface.build_curve(lower_outer, f'{prefix}_LowerOuter')

        # Step 4 - Offset and loft curves
        def loft_offset_curves(curve, name):
            curve_pos = mc.duplicate(curve, name=name + '_pos')[0]
            curve_neg = mc.duplicate(curve, name=name + '_neg')[0]
            mc.move(0, 0.2, 0, curve_pos, r=True)
            mc.move(0, -0.2, 0, curve_neg, r=True)
            surf = mc.loft(curve_pos, curve_neg, ch=True, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0,)[0]
            mc.delete(curve, curve_pos, curve_neg)
            return mc.rename(surf, name + '_surf')
        

        upper_lip_surf = loft_offset_curves(upper_lip_curve, f'{prefix}_UpperLip')
        lower_lip_surf = loft_offset_curves(lower_lip_curve, f'{prefix}_LowerLip')
        #upper_outer_surf = loft_offset_curves(upper_outer_curve, f'{prefix}_UpperOuter')
        #lower_outer_surf = loft_offset_curves(lower_outer_curve, f'{prefix}_LowerOuter')
        rib_offsets = []
        to_remove = [f'{prefix}_L_CornerLip', f'{prefix}_R_CornerLip']
        filtered1 = [item for item in upper_lip if item not in to_remove]
        filtered2 = [item for item in lower_lip if item not in to_remove]
        #Mouth_R_UpperLip_04_R_CTRL_CNST_GRP
        for loc in filtered1:
            parts = loc.split('_')
            for part in parts:
                if part in ['L', 'R', 'M']:
                    side = part
            jnt, ctrl, ctrl_offset = UEface.Simple_joint_and_Control(loc, orient=False, check_side=True, CTRL_Size=.2)
            mc.select(clear=True)
            print(upper_lip_surf)
            mc.select(upper_lip_surf)
            mc.select(f'{loc}_{side}_CTRL_CNST_GRP', add=True)
            mc.UVPin()
            rib_offsets.append(ctrl_offset)
        for loc in filtered2:
            parts = loc.split('_')
            for part in parts:
                if part in ['L', 'R', 'M']:
                    side = part
            jnt, ctrl, ctrl_offset = UEface.Simple_joint_and_Control(loc, orient=False, check_side=True, CTRL_Size=.2)
            mc.select(clear=True)
            mc.select(lower_lip_surf)
            mc.select(f'{loc}_{side}_CTRL_CNST_GRP', add=True)
            mc.UVPin()
            rib_offsets.append(ctrl_offset)
        for loc in to_remove:
            jnt, ctrl, ctrl_offset = UEface.Simple_joint_and_Control(loc, orient=False, check_side=True, CTRL_Size=.2)
            rib_offsets.append(ctrl_offset)
        
        '''
        #outer = upper_outer + lower_outer
        for loc in upper_outer:
            # Create joint
            pos = mc.xform(loc, q=True, ws=True, t=True)
            mc.select(clear=True)
            jnt = mc.joint(name=f'{loc}_JNT')
            UEface.add_to_face_bind_set(jnt)
            mc.xform(jnt, ws=True, t=pos,)
            mc.setAttr(f"{jnt}.radius", .1)
            mc.select(clear=True)
            mc.select(upper_outer_surf)
            mc.select(jnt, add=True)
            mc.UVPin()

        for loc in lower_outer:
            # Create joint
            pos = mc.xform(loc, q=True, ws=True, t=True)
            mc.select(clear=True)
            jnt = mc.joint(name=f'{loc}_JNT')
            UEface.add_to_face_bind_set(jnt)
            mc.xform(jnt, ws=True, t=pos,)
            mc.setAttr(f"{jnt}.radius", .1)
            mc.select(clear=True)
            mc.select(lower_outer_surf)
            mc.select(jnt, add=True)
            mc.UVPin()

        '''
        major_jnts = []
        for loc in [f'{prefix}_M_UpperLip_01', f'{prefix}_M_LowerLip_01', f'{prefix}_L_UpperLip_03', f'{prefix}_L_LowerLip_03', f'{prefix}_R_UpperLip_03', f'{prefix}_R_LowerLip_03', f'{prefix}_L_CornerLip', f'{prefix}_R_CornerLip' ]:
            joint, ctrl, ctrl_offset = UEface.Simple_joint_and_Control(loc, overwrite=True, overwrite_name=f'Major_{loc}', check_side=True, CTRL_Size=.6, bind=False, JNT_Size=.7)
            major_jnts.append(joint)

        loc2 = f'{prefix}_M_center'
        pos = mc.xform(loc2, q=True, ws=True, t=True)
        mc.select(clear=True)
        upper_ctrl, upper_offset = UEface.build_basic_control(
            name='UpperLip_M',
            position=pos,
            size=1,)
        lower_ctrl, lower_offset = UEface.build_basic_control(
            name='LowerLip_M',
            position=pos,
            size=1,)
        
        mc.parent('Major_Mouth_M_UpperLip_01_Mouth_CTRL_CNST_GRP', 'Major_Mouth_L_UpperLip_03_Mouth_CTRL_CNST_GRP', 'Major_Mouth_R_UpperLip_03_Mouth_CTRL_CNST_GRP', upper_ctrl)
        mc.parent('Major_Mouth_M_LowerLip_01_Mouth_CTRL_CNST_GRP', 'Major_Mouth_L_LowerLip_03_Mouth_CTRL_CNST_GRP', 'Major_Mouth_R_LowerLip_03_Mouth_CTRL_CNST_GRP', lower_ctrl)


        #skin_upperOuter = [upper_outer_surf, null_jnt, f'Major_{prefix}_M_UpperLip_01_JNT', f'Major_{prefix}_L_UpperLip_03_JNT', f'Major_{prefix}_R_UpperLip_03_JNT', f'Major_{prefix}_L_CornerLip_JNT', f'Major_{prefix}_R_CornerLip_JNT' ]
        skin_upperLip = [upper_lip_surf,f'Major_{prefix}_M_UpperLip_01_JNT', f'Major_{prefix}_L_UpperLip_03_JNT', f'Major_{prefix}_R_UpperLip_03_JNT', f'Major_{prefix}_L_CornerLip_JNT', f'Major_{prefix}_R_CornerLip_JNT' ]
        #skin_LowerOuter = [lower_outer_surf,null_jnt, f'Major_{prefix}_M_LowerLip_01_JNT', f'Major_{prefix}_L_LowerLip_03_JNT', f'Major_{prefix}_R_LowerLip_03_JNT', f'Major_{prefix}_L_CornerLip_JNT', f'Major_{prefix}_R_CornerLip_JNT' ]
        skin_LowerLip = [lower_lip_surf, f'Major_{prefix}_M_LowerLip_01_JNT', f'Major_{prefix}_L_LowerLip_03_JNT', f'Major_{prefix}_R_LowerLip_03_JNT', f'Major_{prefix}_L_CornerLip_JNT', f'Major_{prefix}_R_CornerLip_JNT' ]

        print(skin_LowerLip)
        mc.select(skin_LowerLip, add=False)
        mc.skinCluster(tsb=True)
        #mc.select(skin_LowerOuter, add=False)
        #mc.skinCluster(tsb=True)
        mc.select(skin_upperLip, add=False)
        mc.skinCluster(tsb=True)
        #mc.select(skin_upperOuter, add=False)
        #mc.skinCluster(tsb=True)

        mc.group(upper_lip_surf, lower_lip_surf, *rib_offsets, 'Major_Mouth_M_UpperLip_01_JNT', 'Major_Mouth_M_LowerLip_01_JNT', 'Major_Mouth_L_UpperLip_03_JNT', 'Major_Mouth_L_LowerLip_03_JNT', 'Major_Mouth_R_UpperLip_03_JNT', 'Major_Mouth_R_LowerLip_03_JNT', 'Major_Mouth_L_CornerLip_JNT', 'Major_Mouth_R_CornerLip_JNT', name='Mouth_Extras_offsets')
        mc.parent('Mouth_Extras_offsets', 'RIG')
        mc.hide(upper_lip_surf, lower_lip_surf, 'Major_Mouth_M_UpperLip_01_JNT', 'Major_Mouth_M_LowerLip_01_JNT', 'Major_Mouth_L_UpperLip_03_JNT', 'Major_Mouth_L_LowerLip_03_JNT', 'Major_Mouth_R_UpperLip_03_JNT', 'Major_Mouth_R_LowerLip_03_JNT', 'Major_Mouth_L_CornerLip_JNT', 'Major_Mouth_R_CornerLip_JNT', )

        for loc in to_remove:
            side = loc.split('_')[1] if '_' in loc else 'Unknown'
            mc.parentConstraint(f'Major_Mouth_{side}_CornerLip_Mouth_CTRL', f'Mouth_{side}_CornerLip_{side}_CTRL_CNST_GRP', mo=True)
            
