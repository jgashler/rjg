import maya.cmds as mc
from importlib import reload
import re

import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.build.guide as rGuide
import rjg.libs.transform as rXform
reload(rAttr)
reload(rChain)
reload(rCtrl)
reload (rGuide)
reload(rXform)

class UEface:
    def __init__(self, part=None, ctrl_scale=1, grp_name=None, guide_list=None):
        self.part = part
        self.base_name = self.part

        self.guide_list = guide_list
        self.ctrl_scale = ctrl_scale
        self.grp_name = grp_name

        if self.guide_list:
            if not isinstance(self.guide_list, list):
                self.guide_list = [self.guide_list]

    @staticmethod
    def get_side_from_guide(guide):
        parts = guide.split('_')
        if len(parts) >= 2 and parts[1]:  # Check if there's a second part and it's not empty
            return parts[1]
        else:
            return 'M'
    
    @staticmethod
    def build_basic_control( name='Main', shape='circle', size=5.0, color_rgb=(1, 1, 0), position=(0, 0, 0), rotation=(0, 0, 0)):
        side = UEface.get_side_from_guide(name)
        rCtrl.ctrl = rCtrl.Control(parent=None, 
                                       shape=shape, 
                                       side=side, 
                                       suffix='CTRL', 
                                       name= name, 
                                       axis='y', 
                                       group_type='main', 
                                       rig_type='primary', 
                                       translate=position, 
                                       rotate=rotation, 
                                       ctrl_scale= size)
        ctrl_name = rCtrl.ctrl.ctrl      # This is the shape transform node (e.g., 'Main_CTRL')
        top_group = rCtrl.ctrl.top       # This is the topmost group (e.g., 'Main_CTRL_OFF')
    
        return ctrl_name, top_group
    
    @staticmethod
    def add_to_face_bind_set(obj_name):
        """
        Adds the specified object to the selection set 'UE_Face_Bind'.
        If the set doesn't exist, it creates it first.

        Args:
            obj_name (str): The name of the object to add to the set.
        """
        set_name = 'UE_Face_Bind'

        if not mc.objExists(set_name):
            mc.sets(name=set_name)
            print(f"Created set: {set_name}")

        if mc.objExists(obj_name):
            mc.sets(obj_name, add=set_name)
            print(f"Added {obj_name} to {set_name}")
        else:
            print(f"Object '{obj_name}' does not exist.")

    @staticmethod
    def Simple_joint_and_Control(
        guide,
        suffix=None,
        orient=True,
        overwrite=False,
        overwrite_name=None,
        scale=True,
        check_side=False,
        CTRL_Color=(0, 0, 1),
        CTRL_Size=0.2,
        JNT_Size=0.5,
        bind = True
    ):
        """
        Creates a joint and control at the guide's position and orientation.

        Args:
            guide (str): Name of the guide object.
            suffix (str or None): Suffix to prepend (e.g. 'Nose'). If None, no suffix added.
            orient (bool): Use guide's rotation for joint/control.
            overwrite (bool): Use overwrite_name instead of guide name.
            overwrite_name (str): Optional. Custom name if overwrite=True.
            scale (bool): Whether to add a scaleConstraint.
            check_side (bool): Enable color override based on '_L_', '_R_', or '_M_' tags.
            CTRL_Color (tuple): RGB color for control (ignored if check_side=True).
            CTRL_Size (float): Control size.
            JNT_Size (float): Joint radius.

        Returns:
            tuple: (joint_name, control_name, control_offset_group)
        """

        if not mc.objExists(guide):
            mc.error(f"Guide '{guide}' does not exist.")
            return

        # Get world transform
        pos = mc.xform(guide, q=True, ws=True, t=True)
        rot = mc.xform(guide, q=True, ws=True, ro=True) if orient else [0, 0, 0]

        # Derive base name for naming
        if overwrite and overwrite_name:
            base_name = overwrite_name
        else:
            base_name = guide
            if suffix:
                # If suffix is part of the guide name, remove it from base_name
                prefix = f"{suffix}_"
                if base_name.startswith(prefix):
                    base_name = base_name[len(prefix):]

        # Build final names
        if suffix:
            joint_name = f"{suffix}_{base_name}_JNT"
            ctrl_name = f"{suffix}_{base_name}"
        else:
            joint_name = f"{base_name}_JNT"
            ctrl_name = f"{base_name}"

        # Determine final control color
        final_color = CTRL_Color
        if check_side:
            if "_L_" in guide:
                final_color = (0, 0, 1)  # Blue
            elif "_R_" in guide:
                final_color = (1, 0, 0)  # Red
            elif "_M_" in guide:
                final_color = (1, 1, 0)  # Yellow

        # Create joint
        mc.select(clear=True)
        jnt = mc.joint(name=joint_name)
        if bind == True:
            UEface.add_to_face_bind_set(jnt)
        mc.xform(jnt, ws=True, t=pos, ro=rot)
        mc.setAttr(f"{jnt}.radius", JNT_Size)

        # Create control
        ctrl, ctrl_offset = UEface.build_basic_control(
            name=ctrl_name,
            size=CTRL_Size,
            color_rgb=final_color,
            position=pos,
            rotation=rot
        )

        # Constrain joint to control
        mc.parentConstraint(ctrl, jnt, mo=True)
        if scale:
            mc.scaleConstraint(ctrl, jnt, mo=True)

        return jnt, ctrl, ctrl_offset
    



    @staticmethod
    def create_driver_joints(controls=None, default_mult=10.0, joint_suffix="_Driver"):
        if not controls:
            mc.warning("No controls provided.")
            return

        for ctrl in controls:
            if not mc.objExists(ctrl):
                mc.warning(f"Control '{ctrl}' does not exist.")
                continue

            # Add DriverMult attribute if it doesn't exist
            if not mc.attributeQuery("DriverMult", node=ctrl, exists=True):
                mc.addAttr(ctrl, longName="DriverMult", attributeType="double", defaultValue=default_mult, keyable=True)

            # Get position of control
            pos = mc.xform(ctrl, query=True, worldSpace=True, translation=True)

            # Create joint at world position, don't inherit rotation
            joint_name = ctrl + joint_suffix

            mc.select(clear=True)
            driver_joint = mc.joint(name=joint_name, position=pos)
            mc.setAttr(driver_joint + ".rotate", 0, 0, 0)
            mc.setAttr(driver_joint + ".radius", 0.1)
            mc.makeIdentity(driver_joint, apply=True, t=1, r=1, s=1, n=0)

            # Create multiplyDivide node
            mult_node = mc.createNode("multiplyDivide", name=f"{ctrl}_DriverMult_node")

            # Connect control translate to multiplyDivide input1
            mc.connectAttr(ctrl + ".translateX", mult_node + ".input1X", force=True)
            mc.connectAttr(ctrl + ".translateY", mult_node + ".input1Y", force=True)
            mc.connectAttr(ctrl + ".translateZ", mult_node + ".input1Z", force=True)

            # Connect DriverMult to input2 (all axes)
            mc.connectAttr(ctrl + ".DriverMult", mult_node + ".input2X", force=True)
            mc.connectAttr(ctrl + ".DriverMult", mult_node + ".input2Y", force=True)
            mc.connectAttr(ctrl + ".DriverMult", mult_node + ".input2Z", force=True)

            # Connect output of mult to joint rotation
            mc.connectAttr(mult_node + ".outputX", driver_joint + ".rotateX", force=True)
            mc.connectAttr(mult_node + ".outputY", driver_joint + ".rotateY", force=True)
            mc.connectAttr(mult_node + ".outputZ", driver_joint + ".rotateZ", force=True)

        print("✅ Driver joints created successfully.")


    @staticmethod
    def chain_parts(
        chain_names,
        jnt_parent=None,
        ctrl_parent=None,
        joints=True,
        controls=True
    ):
        """
        Chains together joints and/or controls based on an ordered list of guide base names.

        Args:
            chain_names (list): List of guide names (e.g., ['feather01_01', 'feather01_02', ...])
            jnt_parent (str or None): Optional. Name of the object to parent the first joint under.
            ctrl_parent (str or None): Optional. Name of the object to parent the first offset group under.
            joints (bool): Whether to chain joints (guide + '_JNT').
            controls (bool): Whether to chain controls (guide + '_GRP' under previous guide + '_CTRL').
        """
        if not chain_names or (not joints and not controls):
            return

        prev_jnt = None
        prev_ctrl = None

        for i, guide in enumerate(chain_names):
            side = guide.split('_')[0] if '_' in guide else 'Unknown'
            jnt_name = f"{guide}_JNT"
            ctrl_name = f"{guide}_{side}_CTRL"
            grp_name = f"{guide}_{side}_CTRL_CNST_GRP"

            # Chain joints
            if joints and mc.objExists(jnt_name):
                if i == 0:
                    if jnt_parent and mc.objExists(jnt_parent):
                        mc.parent(jnt_name, jnt_parent)
                else:
                    if prev_jnt and mc.objExists(prev_jnt):
                        mc.parent(jnt_name, prev_jnt)
                prev_jnt = jnt_name

            # Chain controls (via offset groups)
            if controls and mc.objExists(grp_name):
                if i == 0:
                    if ctrl_parent and mc.objExists(ctrl_parent):
                        mc.parent(grp_name, ctrl_parent)
                else:
                    if prev_ctrl and mc.objExists(prev_ctrl):
                        mc.parent(grp_name, prev_ctrl)
                prev_ctrl = ctrl_name  # we parent GRP, but track CTRL for next

        print(f"[INFO] Chained {'joints' if joints else ''} {'and' if joints and controls else ''} {'controls' if controls else ''} for {len(chain_names)} items.")

    @staticmethod
    def strip_suffix_from_guide(suffix, guide_name):
        """
        Removes the suffix (and underscore) from the start of a guide name,
        and strips the leading underscore from the result (if any).

        Args:
            suffix (str): The suffix/prefix used (e.g. 'Nose').
            guide_name (str): The full guide name (e.g. 'Nose_M_Tip').

        Returns:
            str: The base guide name without the suffix (e.g. 'M_Tip').
        """
        prefix = f"{suffix}_"
        if guide_name.startswith(prefix):
            result = guide_name[len(prefix):]
            return result.lstrip('_')
        return guide_name

    @staticmethod
    def get_prefix_from_group(group_name):
        """
        Extracts the prefix from the guide group name (e.g. 'Nose_guides' -> 'Nose').

        Args:
            group_name (str): The name of the guide group.

        Returns:
            str: The prefix (e.g. 'Nose').
        """
        if not group_name.endswith('_guides'):
            raise ValueError(f"Group name '{group_name}' must end with '_guides'")
        
        return group_name.rsplit('_guides', 1)[0]

    @staticmethod
    def check_guides(group_name, part, guide_basenames):
        """
        Checks if all expected guide transforms exist under a guide group.

        Args:
            group_name (str): The name of the guide group, e.g. "Nose_guides"
            part (str): The guide part name, e.g. "Nose"
            guide_basenames (list): A list of base names, e.g.
                                    ['M_Tip', 'L_Nostril', 'M_NoseRoot', ...]
        """
        if not group_name.endswith('_guides'):
            mc.error(f"Group name '{group_name}' must end with '_guides'")
            return

        if not mc.objExists(group_name):
            mc.error(f"Group '{group_name}' does not exist!")
            return

        suffix = group_name.replace('_guides', '')  # use this as the prefix

        # Build expected guide names
        expected_guides = [f"{suffix}_{name}" for name in guide_basenames]

        # Get children in the group
        children = mc.listRelatives(group_name, children=True, fullPath=False) or []

        # Check for missing
        missing = [guide for guide in expected_guides if guide not in children]

        if missing:
            print("❌ Missing guides:")
            for miss in missing:
                print(f"  - {miss}")
        else:
            print("✅ All expected guides found!")

    @staticmethod
    def build_curve(guide_list, prefix, degree=1):
        """
        Builds a NURBS curve using a list of guide names (in order), with a given prefix.

        Args:
            guide_list (list): Ordered list of guide names (strings).
            prefix (str): Prefix for the curve name (e.g., 'Eyelid', 'Brow', 'Wing').
            degree (int): Degree of the curve (default = 3).

        Returns:
            str: The name of the created curve.
        """
        if not guide_list or len(guide_list) < 2:
            print(f"[WARN] Not enough guides to build a curve for prefix '{prefix}'")
            return None

        # Get world positions from guides
        try:
            points = [mc.xform(g, q=True, ws=True, t=True) for g in guide_list]
        except Exception as e:
            print(f"[ERROR] Failed to query guide transforms: {e}")
            return None

        # Choose linear curve if not enough points for specified degree
        curve_degree = min(degree, len(points) - 1)

        # Build curve
        curve_name = f"{prefix}_curve"
        result = mc.curve(name=curve_name, degree=curve_degree, point=points)
        print(f"[INFO] Created curve: {result}")
        return result
