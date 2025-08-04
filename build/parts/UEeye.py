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

class UEeye(UEface):
    def __init__(self, grp_name=None, ctrl_scale=1,):
        super().__init__(part='Eye', grp_name=grp_name, ctrl_scale=ctrl_scale)
        
    def get_sorted_eyelid_guides(self, prefix):
        prefix = UEface.get_prefix_from_group(self.grp_name)
        all_guides = mc.ls(f'{prefix}_Eyelid_*', type='transform')

        def extract_number(name):
            match = re.search(r'(\d+)', name)
            return int(match.group(1)) if match else 0

        inner_upper = sorted([g for g in all_guides if 'InnerUpper' in g], key=extract_number)
        inner_lower = sorted([g for g in all_guides if 'InnerLower' in g], key=extract_number)
        outer_upper = sorted([g for g in all_guides if 'OuterUpper' in g], key=extract_number)
        outer_lower = sorted([g for g in all_guides if 'OuterLower' in g], key=extract_number)

        mid_upper = [f'{prefix}_Eyelid_Upper']
        mid_lower = [f'{prefix}_Eyelid_Lower']

        inner_corner = [g for g in all_guides if 'InnerCorner' in g]
        outer_corner = [g for g in all_guides if 'OuterCorner' in g]

        upper_list = inner_corner + inner_upper + mid_upper + outer_upper + outer_corner
        lower_list = inner_corner + inner_lower + mid_lower + outer_lower + outer_corner

        # all_eyelid_guides is just all matching transforms, sorted alphabetically or by whatever logic you want
        all_eyelid_guides = sorted(all_guides)

        return upper_list, lower_list, all_eyelid_guides

    def cleanup_eye_rig(self, guide_group_name):
        # Parse suffix from guide group name (e.g. "Eye_L_guides" → "Eye_L")
        parts = guide_group_name.split('_')
        if len(parts) < 3:
            mc.error(f"Invalid guide group name: {guide_group_name}")
            return
        suffix = '_'.join(parts[:2])  # Eye_L or Eye_R or Eye_M
        side = suffix.split('_')[-1]  # L, R, or M

        # Delete specified curves if they exist
        curves_to_delete = [
            f"{guide_group_name}_Eyelid_Upper_CRV",
            f"{guide_group_name}_Eyelid_Lower_CRV",
            f"{guide_group_name}_Eyelid_Upper_CRV_back",
            f"{guide_group_name}_Eyelid_Upper_CRV_front",
            f"{guide_group_name}_Eyelid_Lower_CRV_back",
            f"{guide_group_name}_Eyelid_Lower_CRV_front"
        ]
        for obj in curves_to_delete:
            if mc.objExists(obj):
                mc.delete(obj)
                print(f"Deleted {obj}")

        # Group these into Look_master_group
        look_master_children = [
            "LookNULL_loc",
            f"{suffix}_eyelid_look_loc",
            f"{suffix}_Look_GRP"
        ]

        # Check if Look_master_group exists
        if mc.objExists("Look_master_group"):
            look_master_group = "Look_master_group"
        else:
            # Create at position of eye center guide with x=0
            eye_center_guide = f"{suffix}_EyeCenterPivot"
            if mc.objExists(eye_center_guide):
                pos = mc.xform(eye_center_guide, q=True, ws=True, t=True)
                pos[0] = 0  # set x to 0
            else:
                pos = [0, 0, 0]

            look_master_group = mc.group(empty=True, name="Look_master_group")
            mc.xform(look_master_group, ws=True, t=pos)
            print("Created Look_master_group at eye center pivot with x=0")

        # Parent look_master_children under Look_master_group
        for child in look_master_children:
            if mc.objExists(child):
                try:
                    mc.parent(child, look_master_group)
                    print(f"Parented {child} under {look_master_group}")
                except Exception as e:
                    print(f"Failed to parent {child} under {look_master_group}: {e}")

        # Group these into {suffix}_offset_grp
        offset_grp_children = [
            f"{suffix}_look_offset",
            f"{suffix}_OuterLower01_GRP",
            f"{suffix}_InnerUpper01_GRP",
            f"{suffix}_OuterUpper01_GRP",
            f"{suffix}_OuterCorner_GRP",
            f"{suffix}_InnerLower01_GRP",
            f"{suffix}_Upper_GRP",
            f"{suffix}_InnerCorner_GRP",
            f"{suffix}_Lower_GRP",
            f"{suffix}_Eyelid_Upper_Major_JNT",
            f"{suffix}_Eyelid_InnerCorner_Major_JNT",
            f"{suffix}_Eyelid_OuterCorner_Major_JNT",
            f"{suffix}_Eyelid_Lower_Major_JNT",
            f"{suffix}_guides_Eyelid_Upper_CRV_loft",
            f"{suffix}_guides_Eyelid_Lower_CRV_loft"
        ]

        # Create offset group
        offset_group_name = f"{suffix}_offset_grp"
        if not mc.objExists(offset_group_name):
            offset_grp = mc.group(empty=True, name=offset_group_name)
            print(f"Created {offset_group_name}")
        else:
            offset_grp = offset_group_name

        # Parent offset_grp_children under offset_grp
        for child in offset_grp_children:
            if mc.objExists(child):
                try:
                    mc.parent(child, offset_grp)
                    print(f"Parented {child} under {offset_grp}")
                except Exception as e:
                    print(f"Failed to parent {child} under {offset_grp}: {e}")

        # Parent offset group under RIG group if ROOT and RIG exist
        if mc.objExists("ROOT") and mc.objExists("RIG"):
            try:
                mc.parent(offset_grp, "RIG")
                print(f"Parented {offset_grp} under RIG")
            except Exception as e:
                print(f"Failed to parent {offset_grp} under RIG: {e}")

        # Now handle joints grouping
        joints_to_group = [
            f"{suffix}_Eyelid_OuterUpper01_JNT",
            f"{suffix}_Eyelid_OuterCorner_JNT",
            f"{suffix}_Eyelid_InnerLower01_JNT",
            f"{suffix}_Eyelid_Upper_JNT",
            f"{suffix}_Eyelid_InnerCorner_JNT",
            f"{suffix}_Eyelid_Lower_JNT",
            f"{suffix}_Eyelid_InnerUpper01_JNT",
            f"{suffix}_Eyelid_OuterLower01_JNT",
            f"{suffix}_Socket_InnerLower01_JNT",
            f"{suffix}_Socket_OuterUpper01_JNT",
            f"{suffix}_Socket_InnerCorner_JNT",
            f"{suffix}_Socket_OuterLower01_JNT",
            f"{suffix}_Socket_OuterCorner_JNT",
            f"{suffix}_Socket_Lower_JNT",
            f"{suffix}_Socket_InnerUpper01_JNT",
            f"{suffix}_Socket_Upper_JNT"
        ]

        joints_group_name = f"{suffix}_joints"

        if mc.objExists("ROOT") and mc.objExists("SKEL"):
            # Parent all joints under "head" group if exists
            if mc.objExists("head"):
                for joint in joints_to_group:
                    if mc.objExists(joint):
                        try:
                            mc.parent(joint, "head")
                            print(f"Parented {joint} under head")
                        except Exception as e:
                            print(f"Failed to parent {joint} under head: {e}")
            else:
                print("head group not found; skipping parenting joints under head")
        else:
            # Create joints group if doesn't exist
            if not mc.objExists(joints_group_name):
                joints_grp = mc.group(empty=True, name=joints_group_name)
                print(f"Created {joints_group_name}")
            else:
                joints_grp = joints_group_name

            # Parent joints under joints_grp
            for joint in joints_to_group:
                if mc.objExists(joint):
                    try:
                        mc.parent(joint, joints_grp)
                        print(f"Parented {joint} under {joints_grp}")
                    except Exception as e:
                        print(f"Failed to parent {joint} under {joints_grp}: {e}")


    def create_master_eyelid_control_and_group(self, group_name):
        """
        Builds the master eyelid control first, then parents relevant groups under a new group,
        and parents that group under the master control.

        Args:
            group_name (str): The guide group name (e.g., 'Eye_L_guides').
        """
        if not mc.objExists(group_name):
            mc.error(f"Group '{group_name}' does not exist.")
            return

        parts = group_name.split('_')
        if len(parts) < 3:
            mc.error(f"Group name '{group_name}' doesn't follow expected pattern.")
            return

        suffix = '_'.join(parts[:2])  # Eye_L or Eye_R or Eye_M
        side = suffix.split('_')[-1]
        eye_center = f"{suffix}_EyeCenterPivot"

        if not mc.objExists(eye_center):
            mc.error(f"Guide '{eye_center}' not found.")
            return

        # Get EyeCenterPivot position and rotation
        pos = mc.xform(eye_center, q=True, ws=True, t=True)
        rot = mc.xform(eye_center, q=True, ws=True, ro=True)

        # Build Master Control at EyeCenterPivot first
        ctrl_name = f"{suffix}_MasterControl"
        if mc.objExists(ctrl_name):
            mc.delete(ctrl_name)

        # Determine color
        if side == 'L':
            ctrl_color = (0, 0, 1)  # Blue
        elif side == 'R':
            ctrl_color = (1, 0, 0)  # Red
        else:
            ctrl_color = (1, 1, 0)  # Yellow
        ctrl, ctrl_offset_grp = UEface.build_basic_control(
            name=ctrl_name,
            size=1.0,
            color_rgb=ctrl_color,
            position=pos,
            rotation=(0,0,0)
        )

        # Create a group to hold the eyelid parts, at same position as control
        eyelid_grp_name = f"{suffix}_eyelid_grp"
        if mc.objExists(eyelid_grp_name):
            mc.delete(eyelid_grp_name)
        eyelid_grp = mc.group(empty=True, name=eyelid_grp_name)
        mc.xform(eyelid_grp, ws=True, t=pos, ro=rot)

        # List of objects to parent
        objects_to_parent = [
            f'{suffix}_Socket_Upper_GRP',
            f'{suffix}_Socket_InnerUpper01_GRP',
            f'{suffix}_Socket_Lower_GRP',
            f'{suffix}_Socket_OuterCorner_GRP',
            f'{suffix}_Socket_OuterLower01_GRP',
            f'{suffix}_Socket_InnerCorner_GRP',
            f'{suffix}_Socket_OuterUpper01_GRP',
            f'{suffix}_Socket_InnerLower01_GRP',
            f'{suffix}_Eyelid_Lower_BlinkOffset3',
            f'{suffix}_InnerCorner_Major_GRP',
            f'{suffix}_Eyelid_Upper_BlinkOffset3',
            f'{suffix}_OuterCorner_Major_GRP'
        ]

        for obj in objects_to_parent:
            if mc.objExists(obj):
                mc.parent(obj, eyelid_grp)
            else:
                print(f"Warning: Object '{obj}' not found. Skipping.")

        # Parent the eyelid group under the master control's offset group
        mc.parent(eyelid_grp, ctrl_offset_grp)

        # Create an extra offset group above ctrl_offset_grp
        extra_offset_name = f"{suffix}_look_offset"
        if mc.objExists(extra_offset_name):
            mc.delete(extra_offset_name)

        extra_offset_grp = mc.group(empty=True, name=extra_offset_name)
        pos_ctrl_offset = mc.xform(ctrl_offset_grp, q=True, ws=True, t=True)
        rot_ctrl_offset = mc.xform(ctrl_offset_grp, q=True, ws=True, ro=True)
        mc.xform(extra_offset_grp, ws=True, t=pos_ctrl_offset, ro=rot_ctrl_offset)

        # Parent ctrl_offset_grp under extra offset group
        mc.parent(ctrl_offset_grp, extra_offset_grp)

        print(f"Created master eyelid control '{ctrl_name}', grouped eyelids in '{eyelid_grp_name}', and set up offset groups.")


    def build_blink_system(self, group_name):
        # Parse base prefix like "L_eye" from "L_eye_guides"
        parts = group_name.split('_')
        if len(parts) < 3 or parts[-1] != 'guides':
            mc.error("Invalid group name")
        side = parts[0]
        prefix = parts[1]
        base = f"{side}_{prefix}"

        # Get guide names
        guides = mc.listRelatives(group_name, children=True, type='transform') or []

        required_suffixes = ['Upper', 'Lower', 'InnerCorner', 'OuterCorner']
        eyelid_guides = [g for g in guides if any(g.endswith(s) for s in required_suffixes) and 'Eyelid' in g]
        center_pivot = f"{base}_EyeCenterPivot"

        if not mc.objExists(center_pivot):
            mc.error("Missing EyeCenterPivot")

        center_pos = mc.xform(center_pivot, q=True, ws=True, t=True)
        center_rot = mc.xform(center_pivot, q=True, ws=True, ro=True)

        for guide in eyelid_guides:
            pos = mc.xform(guide, q=True, ws=True, t=True)
            side = guide.split('_')[0]

            #ctrl_color = (0, 0, 1) if side == 'L' else (1, 0, 0) if side == 'R' else (1, 1, 0)
            ctrl_temp = guide.replace('guides', 'ctrl').replace('Eyelid_', '')
            ctrl_name = f'{ctrl_temp}_Major'
            ctrl, offset = UEface.build_basic_control(ctrl_name, size=0.4, position=pos, rotation=(0, 0, 0))

            # Create joint
            jnt_temp = guide.replace('guides', 'JNT')
            jnt_name = f'{jnt_temp}_Major_JNT'
            mc.select(clear=True)
            jnt = mc.joint(name=jnt_name, rad=.2)
            mc.xform(jnt, ws=True, t=pos, ro=(0, 0, 0))

            mc.parent(ctrl, offset)
            mc.parentConstraint(ctrl, jnt_name, mo=True)
            mc.scaleConstraint(ctrl, jnt_name, mo=True)


            if guide.endswith('Upper') or guide.endswith('Lower'):
                # BlinkOffset group at center pivot
                blink_offset = f"{guide}_BlinkOffset"
                blink_grp = mc.group(empty=True, name=blink_offset)
                mc.xform(blink_grp, ws=True, t=center_pos, ro=center_rot)
                #mc.parent(offset, blink_grp)
                blink_trans = f"{guide}_BlinkTransOffset"
                blink2_grp = mc.group(empty=True, name=blink_trans)
                mc.xform(blink2_grp, ws=True, t=center_pos, ro=center_rot)
                #mc.parent(offset, blink_grp)
                blink_offset3 = f"{guide}_BlinkOffset3"
                blink3_grp = mc.group(empty=True, name=blink_offset3)
                mc.xform(blink3_grp, ws=True, t=center_pos)
                #mc.parent(offset, blink_grp)

                # Add attribute
                if not mc.attributeQuery('blink_mult', node=ctrl, exists=True) and side =="R":
                    mc.addAttr(ctrl, longName='blink_mult', attributeType='double', defaultValue=10.0, keyable=True)
                if not mc.attributeQuery('blink_mult2', node=ctrl, exists=True) and guide.endswith('Upper') and side =="R":
                    mc.addAttr(ctrl, longName='blink_mult2', attributeType='double', defaultValue=-0.05, keyable=True)
                if not mc.attributeQuery('blink_mult2', node=ctrl, exists=True) and guide.endswith('Lower') and side =="R":
                    mc.addAttr(ctrl, longName='blink_mult2', attributeType='double', defaultValue=0.05, keyable=True)

                if not mc.attributeQuery('blink_mult', node=ctrl, exists=True):
                    mc.addAttr(ctrl, longName='blink_mult', attributeType='double', defaultValue=-10.0, keyable=True)
                if not mc.attributeQuery('blink_mult2', node=ctrl, exists=True) and guide.endswith('Upper'):
                    mc.addAttr(ctrl, longName='blink_mult2', attributeType='double', defaultValue=-0.05, keyable=True)
                if not mc.attributeQuery('blink_mult2', node=ctrl, exists=True) and guide.endswith('Lower'):
                    mc.addAttr(ctrl, longName='blink_mult2', attributeType='double', defaultValue=0.05, keyable=True)
                if side == 'R':
                    mc.setAttr(f"{prefix}_Upper_Major_R_CTRL.blink_mult", 10)
                    mc.setAttr(f"{prefix}_Lower_Major_R_CTRL.blink_mult", 10)


                # Inverse offset group (matches original offset group)
                inverse_offset = f"{guide}_inverse"
                inverse_grp = mc.group(empty=True, name=inverse_offset)
                mc.xform(inverse_grp, ws=True, t=pos, ro=(0, 0, 0))
                mc.delete(mc.parentConstraint(offset, inverse_grp))
                mc.parent(inverse_grp, offset)
                mc.parent(ctrl, inverse_grp)
                mc.parent(blink2_grp, blink3_grp)
                mc.parent(blink_grp, blink2_grp)
                mc.parent(offset, blink_grp)

                # MultiplyDivide nodes
                mult_node = mc.createNode('multiplyDivide', name=f"{guide}_multDiv")
                mult2_node = mc.createNode('multiplyDivide', name=f"{guide}_multDiv2")
                inverse_mult = mc.createNode('multiplyDivide', name=f"{guide}_inverseMultDiv")

                # Connect translateY → mult → rotateX
                mc.connectAttr(f"{ctrl}.translateY", f"{mult_node}.input1X")
                mc.connectAttr(f"{ctrl}.blink_mult", f"{mult_node}.input2X")
                mc.connectAttr(f"{mult_node}.outputX", f"{blink_grp}.rotateX")

                # Connect translateY → mult → rotateX
                mc.connectAttr(f"{ctrl}.translateY", f"{mult2_node}.input1X")
                mc.connectAttr(f"{ctrl}.blink_mult2", f"{mult2_node}.input2X")
                mc.connectAttr(f"{mult2_node}.outputX", f"{blink2_grp}.translateZ")

                # Connect inverse translateY * -1 → translateY
                mc.connectAttr(f"{ctrl}.translateY", f"{inverse_mult}.input1Y")
                mc.setAttr(f"{inverse_mult}.input2Y", -1)
                mc.connectAttr(f"{inverse_mult}.outputY", f"{inverse_grp}.translateY")

            print(f"Built blink system for {guide}")
        mc.parentConstraint(f"{side}_{prefix}_OuterCorner_Major_{prefix}_CTRL", f"{side}_{prefix}_Eyelid_OuterCorner_{prefix}_CTRL_CNST_GRP" )
        mc.parentConstraint(f"{side}_{prefix}_InnerCorner_Major_{prefix}_CTRL", f"{side}_{prefix}_Eyelid_InnerCorner_{prefix}_CTRL_CNST_GRP" )


    def build_eye_look_control_from_guides(self, guide_group_name):
        # Validate guide group name ends with '_guides'
        if not guide_group_name.endswith('_guides'):
            mc.error("Guide group name must end with '_guides'")
            return

        # Extract suffix by removing '_guides'
        suffix = guide_group_name[:-7]  # strips last 7 chars: '_guides'
        side = suffix.split('_')[-1].upper()

        center_pivot_guide = f"{suffix}_EyeCenterPivot"
        aim_guide = f"{suffix}_Aim"
        eyelid_look_loc_name = f"{suffix}_eyelid_look_loc"
        looknull_loc_name = "LookNULL_loc"
        master_ctrl_grp = f"{suffix}_MasterControl_{side}_GRP"

        # Get positions of guides
        pos_center = mc.xform(center_pivot_guide, q=True, ws=True, t=True)
        pos_aim = mc.xform(aim_guide, q=True, ws=True, t=True)

        # Create eye joint at center pivot
        eye_joint = mc.joint(name=f"{suffix}_JNT", position=pos_center, orientation=[0,0,0])
        pupil_joint = mc.joint(name=f"{suffix}pupil_JNT", position=pos_center, orientation=[0,0,0], rad=.5)
        iris_joint = mc.joint(name=f"{suffix}iris_JNT", position=pos_center, orientation=[0,0,0], rad =.5)
        mc.parent(pupil_joint, eye_joint)
        mc.parent(iris_joint, eye_joint)

        look_ctrl_name = f"{suffix}_Look"
        look_ctrl, look_ctrl_offset = UEface.build_basic_control(
            name=look_ctrl_name,
            size=1.0,
            position=pos_aim,
            rotation=(0, 0, 0)
        )
        
        # Rotate look control offset group X by 90 degrees
        mc.setAttr(f"{look_ctrl_offset}.rotateX", 90)
        
        # Create eyelid look locator at look control position
        eyelid_look_loc = mc.spaceLocator(name=eyelid_look_loc_name)[0]
        mc.xform(eyelid_look_loc, ws=True, translation=pos_aim)
        
        # Create or reference LookNULL_loc at same pos but X=0
        if mc.objExists(looknull_loc_name):
            looknull_loc = looknull_loc_name
        else:
            looknull_loc = mc.spaceLocator(name=looknull_loc_name)[0]
            pos_with_zero_x = [0, pos_aim[1], pos_aim[2]]
            mc.xform(looknull_loc, ws=True, translation=pos_with_zero_x)
        
        # Aim constraint from look control to eye joint (maintain offset)
        mc.aimConstraint(look_ctrl, eye_joint, maintainOffset=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType="scene")
        mc.pointConstraint(f'{suffix}_MasterControl_{side}_CTRL', f'{suffix}_JNT', maintainOffset=True,)
        # Parent look control offset and LookNULL_loc under eyelid look locator
        mc.parentConstraint(look_ctrl, eyelid_look_loc, maintainOffset=True)
        mc.parentConstraint(looknull_loc, eyelid_look_loc, maintainOffset=True)
        mc.setAttr(f"{suffix}_eyelid_look_loc_parentConstraint1.{suffix}_Look_{side}_CTRLW0", 0.05)
        # Aim constraint from eyelid look locator to master control group
        if mc.objExists(master_ctrl_grp):
            mc.aimConstraint(eyelid_look_loc, master_ctrl_grp, maintainOffset=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType="scene")
        else:
            print(f"Warning: Master control group '{master_ctrl_grp}' not found, skipping aimConstraint.")


    def build_socket_controls_and_joints(self, group_name):
        """
        For all 'Socket' guides in the group, create a joint and control,
        then parentConstraint and scaleConstraint the joint to the control.
        Naming convention:
        - Controls: {base}_{side}_CTRL
        - Offset groups: {base}_{side}_CTRL_CNST_GRP
        """
        if not mc.objExists(group_name):
            mc.error(f"Group '{group_name}' does not exist.")
            return

        children = mc.listRelatives(group_name, children=True, type='transform') or []

        def extract_info(name):
            # Expected name format: {base}_{side}_Socket{optionalNumber} or similar
            # We'll try to parse side and base prefix properly
            parts = name.split('_')
            if len(parts) < 3:
                return None, None, None, None, None  # invalid format
            side = parts[1]  # usually 'L', 'R', or 'M'
            prefix = parts[0]  # e.g. 'Eye' or 'Face' or 'Head'
            part = parts[2]    # should be 'Socket' here
            guide_name = '_'.join(parts[3:]) if len(parts) > 3 else ''

            # Extract base name and number if any from guide_name
            match = re.match(r"([A-Za-z]+)(\d*)", guide_name)
            if not match:
                base_name = guide_name
                number = None
            else:
                base_name = match.group(1)
                number = int(match.group(2)) if match.group(2) else None
            return side, prefix, part, base_name, number

        for guide in children:
            if not mc.objExists(guide):
                continue

            side, prefix, part, base_name, number = extract_info(guide)
            if side is None or part != 'Socket':
                continue

            pos = mc.xform(guide, q=True, ws=True, t=True)
            rot = [0, 0, 0]

            # Joint name: {guide}_JNT
            jnt_name = f"{guide}_JNT"
            mc.select(clear=True)
            jnt = mc.joint(name=jnt_name, rad=0.1)
            mc.xform(jnt, ws=True, t=pos, ro=rot)
            UEface.add_to_face_bind_set(jnt)

            # Control naming: {prefix}_{side}_Socket_CTRL (or you can keep the guide name with _CTRL suffix)
            ctrl_name = f"{prefix}_{side}_Socket_CTRL"
            # But if you want unique control per guide, just append base_name or number:
            if base_name:
                ctrl_name = f"{prefix}_{side}_Socket_{base_name}_CTRL"
                if number is not None:
                    ctrl_name += f"{number:02d}"

            # Control color by side
            if side == 'L':
                ctrl_color = (0, 0, 1)  # Blue
            elif side == 'R':
                ctrl_color = (1, 0, 0)  # Red
            else:
                ctrl_color = (1, 1, 0)  # Yellow

            ctrl, offset_grp = UEface.build_basic_control(
                name=ctrl_name,
                size=0.2,
                color_rgb=ctrl_color,
                position=pos,
                rotation=rot
            )

            # Rotate offset_grp's X 90 degrees to match orientation if needed
            mc.setAttr(f"{offset_grp}.rotateX", 90)

            # Parent and scale constrain joint to control
            try:
                mc.parentConstraint(ctrl, jnt, mo=True)
                mc.scaleConstraint(ctrl, jnt, mo=True)
                print(f"Constrained {jnt} to {ctrl}")
            except Exception as e:
                print(f"Constraint failed for {ctrl} → {jnt}: {e}")
    def build(self):
        
        prefix = UEface.get_prefix_from_group(self.grp_name)
        #Get Eyelid Order
        #Order {Prefix}_Eyelid_InnerCorner, {Prefix}_Eyelid_Inner{Upper or Lower}01, (and more), {Prefix}_Eyelid_{Upper or Lower}, (and more) {Prefix}_Eyelid_Outer{Upper or Lower}01, {Prefix}_Eyelid_OuterCorner
        upper_guides, lower_guides, all_eyelids = self.get_sorted_eyelid_guides(prefix)

        upper_curve = UEface.build_curve(upper_guides, f'{prefix}_Upper', degree=1)
        lower_curve = UEface.build_curve(lower_guides, f'{prefix}_Lower', degree=1)
        surfs = []

        for curve in [upper_curve, lower_curve]:
            dup_curve = mc.duplicate(curve)[0]  # duplicate returns a list
            mc.move(0, 0, 0.1, dup_curve, relative=True)  # move it slightly in Z
            loft_surface = mc.loft(curve, dup_curve, ch=False, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0, rsn=True)[0]
            loft_surface = mc.rename(loft_surface, f"{prefix}_{curve}_ribbon")
            surfs.append(loft_surface)
            mc.delete(curve, dup_curve)

        upper_pin = [item for item in all_eyelids if item not in lower_guides]
        lower_pin = [item for item in all_eyelids if item not in upper_guides]

        eyelid_jnts =[]
        eyelid_ctrls = []
        eyelid_offsets = []
        
        eyelid_grp = mc.group(name=f"{prefix}_eyelid_Control_GRP", empty=True)
        for guide in all_eyelids:
            jnt, ctrl, ctrl_offset = UEface.Simple_joint_and_Control(
                guide,
                orient=True,
                overwrite=False,
                overwrite_name=None,
                scale=False,
                check_side=False,
                CTRL_Size=0.2,
                JNT_Size=0.5,
                bind = True)
            
            if guide in upper_pin:
                mc.select(clear=True)
                mc.select(surfs[0])
                mc.select(ctrl_offset, add=True)
                mc.UVPin()
            elif guide in lower_pin:
                mc.select(clear=True)
                mc.select(surfs[1])
                mc.select(ctrl_offset, add=True)
                mc.UVPin()
            else:
                mc.xform(ctrl_offset, ro=[90,0,0])
            eyelid_jnts.append(jnt)
            eyelid_ctrls.append(ctrl)
            eyelid_offsets.append(ctrl_offset)
            mc.parent(ctrl_offset, eyelid_grp)

        #Major Controls
        '''
        major_eyelid_jnts =[]
        major_eyelid_ctrls = []
        major_eyelid_offsets = []
        for guide in [f'{prefix}_Eyelid_Upper', f'{prefix}_Eyelid_Lower', f'{prefix}_Eyelid_InnerCorner', f'{prefix}_Eyelid_OuterCorner' ]:
            jnt, ctrl, ctrl_offset = UEface.Simple_joint_and_Control(
                guide,
                suffix=None,
                orient=False,
                overwrite=True,
                overwrite_name=f'major_{guide}',
                scale=False,
                check_side=False,
                CTRL_Size=0.2,
                JNT_Size=0.5,
                bind = False)
            major_eyelid_jnts.append(jnt)
            major_eyelid_ctrls.append(ctrl)
            major_eyelid_offsets.append(ctrl_offset)
            '''
        
        #Skin to ribbons
        #mc.select(surfs[0], f'{prefix}_Eyelid_Upper', f'{prefix}_Eyelid_InnerCorner', f'{prefix}_Eyelid_OuterCorner', add=False)
        #mc.skinCluster([f'{prefix}_Eyelid_Upper_JNT', f'{prefix}_Eyelid_InnerCorner_JNT', f'{prefix}_Eyelid_OuterCorner_JNT'],surfs[0], toSelectedBones=True)
        #mc.select(surfs[1], f'{prefix}_Eyelid_Lower', f'{prefix}_Eyelid_InnerCorner', f'{prefix}_Eyelid_OuterCorner', add=False)
        #mc.skinCluster([f'{prefix}_Eyelid_Lower_JNT', f'{prefix}_Eyelid_InnerCorner_JNT', f'{prefix}_Eyelid_OuterCorner_JNT'], surfs[1], toSelectedBones=True)

        self.build_blink_system(f'{prefix}_guides')
        self.build_socket_controls_and_joints(f'{prefix}_guides')
        self.create_master_eyelid_control_and_group(f'{prefix}_guides')
        self.build_eye_look_control_from_guides(f'{prefix}_guides')
        #self.cleanup_eye_rig(f'{prefix}_guides')
        mc.skinCluster([f'{prefix}_Eyelid_Upper_Major_JNT', f'{prefix}_Eyelid_InnerCorner_Major_JNT', f'{prefix}_Eyelid_OuterCorner_Major_JNT'], surfs[0], toSelectedBones=True)
        mc.skinCluster([f'{prefix}_Eyelid_Lower_Major_JNT', f'{prefix}_Eyelid_InnerCorner_Major_JNT', f'{prefix}_Eyelid_OuterCorner_Major_JNT'], surfs[1], toSelectedBones=True)
        
        side = prefix.split('_')[-1]  # Takes the part after the underscore
        print(side)  # Output: L

        Joint_to_parent = guide_names = [
            f"{prefix}_Eyelid_InnerCorner_JNT",
            f"{prefix}_Eyelid_InnerLower01_JNT",
            f"{prefix}_Eyelid_InnerUpper01_JNT",
            f"{prefix}_Eyelid_Lower_JNT",
            f"{prefix}_Eyelid_OuterCorner_JNT",
            f"{prefix}_Eyelid_OuterLower01_JNT",
            f"{prefix}_Eyelid_OuterUpper01_JNT",
            f"{prefix}_Eyelid_Upper_JNT",
            f"{prefix}_Eyelid_InnerCorner_Major_JNT",
            f"{prefix}_Eyelid_Lower_Major_JNT",
            f"{prefix}_Socket_InnerLower01_JNT",
            f"{prefix}_Socket_OuterUpper01_JNT",
            f"{prefix}_Socket_InnerCorner_JNT",
            f"{prefix}_Socket_OuterLower01_JNT",
            f"{prefix}_Socket_OuterCorner_JNT",
            f"{prefix}_Socket_Lower_JNT",
            f"{prefix}_Socket_InnerUpper01_JNT",
            f"{prefix}_Socket_Upper_JNT",
            f"{prefix}_JNT"
        ]

        look_to_parent = [
            f"{prefix}_Look_L_CTRL_CNST_GRP",
            f"{prefix}_eyelid_look_loc",
        ] #"LookNULL_loc"

        sockets_to_parent = [
            f"{prefix}_Socket_InnerLower_CTRL01_{side}_CTRL_CNST_GRP",
            f"{prefix}_Socket_OuterUpper_CTRL01_{side}_CTRL_CNST_GRP",
            f"{prefix}_Socket_InnerCorner_CTRL_{side}_CTRL_CNST_GRP",
            f"{prefix}_Socket_OuterLower_CTRL01_{side}_CTRL_CNST_GRP",
            f"{prefix}_Socket_OuterCorner_CTRL_{side}_CTRL_CNST_GRP",
            f"{prefix}_Socket_Lower_CTRL_{side}_CTRL_CNST_GRP",
            f"{prefix}_Socket_InnerUpper_CTRL01_{side}_CTRL_CNST_GRP",
            f"{prefix}_Socket_Upper_CTRL_{side}_CTRL_CNST_GRP"
        ]
        socket_grp = mc.group(*sockets_to_parent, name=f'{prefix}_socket_controls')
        mc.parent(socket_grp, f'{prefix}_MasterControl_{side}_CTRL')
        mc.parent(f'{prefix}_InnerCorner_Major_{side}_CTRL_CNST_GRP', f'{prefix}_OuterCorner_Major_{side}_CTRL_CNST_GRP', f'{prefix}_eyelid_grp')
        mc.parent(f'{prefix}_eyelid_grp', f'{prefix}_MasterControl_{side}_CTRL')
        mc.aimConstraint(f'{prefix}_eyelid_look_loc', f'{prefix}_look_offset', mo = True)
        mc.group(surfs[0], surfs[1], f'{prefix}_eyelid_Control_GRP', f'{prefix}_Eyelid_OuterCorner_Major_JNT', f'{prefix}_Eyelid_Upper_Major_JNT',f'{prefix}_Eyelid_InnerCorner_Major_JNT',f'{prefix}_Eyelid_Lower_Major_JNT', name=f'{prefix}_eyelid_extra_offset')
        mc.parent(f'{prefix}_eyelid_extra_offset', 'RIG')

        mc.hide(surfs[0], surfs[1],)


            

            

        



    
