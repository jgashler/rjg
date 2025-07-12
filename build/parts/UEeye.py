#### JUst First trying to build an outrigger that builds the system with guides will later convert to fit in RJG 

import maya.cmds as mc
import re

def build_basic_control(name='Main', shape='circle', size=5.0, color_rgb=(1, 1, 0), position=(0, 0, 0), rotation=(0, 0, 0)):
    """
    Builds a basic control with an offset group. The offset group holds the transform.
    Uses RGB override color instead of color index.

    Args:
        name (str): Control name.
        shape (str): Shape type (currently just 'circle' supported).
        size (float): Size of the control.
        color_rgb (tuple): RGB color override.
        position (tuple): World position (x, y, z).
        rotation (tuple): World rotation (x, y, z).

    Returns:
        ctrl (str): The name of the control.
        offset_grp (str): The name of the offset group.
    """
    # Create the control
    ctrl = mc.circle(name=f'{name}_CTRL', normal=[0, 1, 0], radius=size, ch=False)[0]

    # Create offset group
    offset_grp = mc.group(empty=True, name=f"{name}_GRP")
    mc.parent(ctrl, offset_grp)

    # Apply world-space transform to the group
    mc.xform(offset_grp, ws=True, translation=position, rotation=rotation)

    # Set control color using RGB
    mc.setAttr(f"{ctrl}.overrideEnabled", 1)
    mc.setAttr(f"{ctrl}.overrideRGBColors", 1)
    mc.setAttr(f"{ctrl}.overrideColorRGB", color_rgb[0], color_rgb[1], color_rgb[2], type="double3")
    return ctrl, offset_grp

    #build_basic_control(name='name', size=10, color_rgb=(1,1,0), position=(0,0,0), rotation=(0,0,0))

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

def check_eye_guides(group_name):
    # Parse side and prefix from group name (expects format: side_prefix_guides)
    parts = group_name.split('_')
    if len(parts) < 3 or parts[-1] != 'guides':
        mc.error(f"Group name '{group_name}' doesn't follow expected pattern: {{side}}_{{prefix}}_guides")
        return

    side = parts[0]
    prefix = parts[1]

    # Expected guides lists
    eyelid_guides = [
        'InnerCorner',
        'InnerUpper01',
        'Upper',
        'OuterUpper01',
        'OuterCorner',
        'OuterLower01',
        'Lower',
        'InnerLower01'
    ]

    socket_guides = [
        'InnerCorner',
        'InnerUpper01',
        'Upper',
        'OuterUpper01',
        'OuterCorner',
        'OuterLower01',
        'Lower',
        'InnerLower01'
    ]

    # Build full expected guide names
    expected_guides = []

    for part in ['Eyelid', 'Socket']:
        for name in eyelid_guides if part == 'Eyelid' else socket_guides:
            expected_guides.append(f"{side}_{prefix}_{part}_{name}")

    # Add the two special guides
    expected_guides += [
        f"{side}_{prefix}_EyeCenterPivot",
        f"{side}_{prefix}_Aim"
    ]

    # Get all children under group
    if not mc.objExists(group_name):
        mc.error(f"Group '{group_name}' does not exist!")
        return

    children = mc.listRelatives(group_name, children=True, fullPath=False) or []

    # Check missing
    missing = [guide for guide in expected_guides if guide not in children]

    if missing:
        print("Missing guides:")
        for miss in missing:
            print(f"  - {miss}")
    else:
        print("All expected guides found!")

def make_loft(curve_list, offset=0.1):
    loft_surfaces = []
    for curve in curve_list:
        if not mc.objExists(curve):
            print(f"Curve '{curve}' does not exist, skipping.")
            continue
        
        # Duplicate twice
        back_curve = mc.duplicate(curve, name=curve + '_back')[0]
        front_curve = mc.duplicate(curve, name=curve + '_front')[0]
        
        # Move duplicates on Z axis
        mc.move(0, 0, -offset, back_curve, relative=True, objectSpace=True)
        mc.move(0, 0, offset, front_curve, relative=True, objectSpace=True)
        
        # Loft between back and front curves
        loft_name = curve + '_loft'
        loft_surface = mc.loft(back_curve, front_curve, name=loft_name, ch=False, uniform=True, close=False, autoReverse=True, degree=3)[0]
        
        loft_surfaces.append(loft_surface)
    
    return loft_surfaces

def build_socket_controls_and_joints(group_name):
    """
    For all 'Socket' guides in the group, create a joint and control,
    then parent and scale constrain the joint to the control.
    """
    if not mc.objExists(group_name):
        mc.error(f"Group '{group_name}' does not exist.")
        return

    children = mc.listRelatives(group_name, children=True, type='transform') or []

    def extract_info(name):
        parts = name.split('_')
        side = parts[0]
        prefix = parts[1]
        part = parts[2]
        guide_name = '_'.join(parts[3:])
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

        if part != 'Socket':
            continue

        pos = mc.xform(guide, q=True, ws=True, t=True)
        rot = [0, 0, 0]

        # Create joint
        jnt_name = f'{guide}_JNT'
        mc.select(clear=True)
        jnt = mc.joint(name=jnt_name, rad=.1)
        mc.xform(jnt, ws=True, t=pos, ro=rot)
        add_to_face_bind_set(jnt)

        # Determine color
        if side == 'L':
            ctrl_color = (0, 0, 1)  # Blue
        elif side == 'R':
            ctrl_color = (1, 0, 0)  # Red
        else:
            ctrl_color = (1, 1, 0)  # Yellow

        # Create control
        ctrl_name = guide
        ctrl, offset_grp = build_basic_control(
            name=ctrl_name, size=0.2, color_rgb=ctrl_color,
            position=pos, rotation=rot
        )
        mc.setAttr(f'{offset_grp}.rotateX', 90)
        # Constrain joint to control
        try:
            mc.parentConstraint(ctrl, jnt, mo=True)
            mc.scaleConstraint(ctrl, jnt, mo=True)
            print(f"Constrained {jnt} to {ctrl}")
        except Exception as e:
            print(f"Constraint failed for {ctrl} → {jnt}: {e}")

def create_master_eyelid_control_and_group(group_name):
    """
    Builds the master eyelid control first, then parents relevant groups under a new group,
    and parents that group under the master control.

    Args:
        group_name (str): The guide group name (e.g., 'L_eye_guides').
    """
    if not mc.objExists(group_name):
        mc.error(f"Group '{group_name}' does not exist.")
        return

    parts = group_name.split('_')
    if len(parts) < 2:
        mc.error(f"Group name '{group_name}' doesn't follow expected pattern.")
        return

    suffix = parts[0]  # e.g. 'L'
    eye_center = f"{suffix}_{parts[1]}_EyeCenterPivot"

    if not mc.objExists(eye_center):
        mc.error(f"Guide '{eye_center}' not found.")
        return

    # Get EyeCenterPivot position and rotation
    pos = mc.xform(eye_center, q=True, ws=True, t=True)
    rot = mc.xform(eye_center, q=True, ws=True, ro=True)

    # Build Master Control at EyeCenterPivot first
    ctrl_name = f"{suffix}_{parts[1]}_MasterControl"
    if mc.objExists(ctrl_name):
        mc.delete(ctrl_name)

    # Determine color
    if suffix == 'L':
        ctrl_color = (0, 0, 1)  # Blue
    elif suffix == 'R':
        ctrl_color = (1, 0, 0)  # Red
    else:
        ctrl_color = (1, 1, 0)  # Yellow
    ctrl, ctrl_offset_grp = build_basic_control(
        name=ctrl_name,
        size=1.0,
        color_rgb=ctrl_color,
        position=pos,
        rotation=(0,0,0)
    )

    # Create a group to hold the eyelid parts, at same position as control
    eyelid_grp_name = f"{suffix}_{parts[1]}_eyelid_grp"
    if mc.objExists(eyelid_grp_name):
        mc.delete(eyelid_grp_name)
    eyelid_grp = mc.group(empty=True, name=eyelid_grp_name)
    mc.xform(eyelid_grp, ws=True, t=pos, ro=rot)

    # List of objects to parent
    objects_to_parent = [
        f'{suffix}_{parts[1]}_Socket_Upper_GRP',
        f'{suffix}_{parts[1]}_Socket_InnerUpper01_GRP',
        f'{suffix}_{parts[1]}_Socket_Lower_GRP',
        f'{suffix}_{parts[1]}_Socket_OuterCorner_GRP',
        f'{suffix}_{parts[1]}_Socket_OuterLower01_GRP',
        f'{suffix}_{parts[1]}_Socket_InnerCorner_GRP',
        f'{suffix}_{parts[1]}_Socket_OuterUpper01_GRP',
        f'{suffix}_{parts[1]}_Socket_InnerLower01_GRP',
        f'{suffix}_{parts[1]}_Eyelid_Lower_BlinkOffset3',
        f'{suffix}_{parts[1]}_InnerCorner_Major_GRP',
        f'{suffix}_{parts[1]}_Eyelid_Upper_BlinkOffset3',
        f'{suffix}_{parts[1]}_OuterCorner_Major_GRP'
    ]

    for obj in objects_to_parent:
        if mc.objExists(obj):
            mc.parent(obj, eyelid_grp)
        else:
            print(f"Warning: Object '{obj}' not found. Skipping.")

    # Parent the eyelid group under the master control's offset group
    mc.parent(eyelid_grp, ctrl)

    # Create an extra offset group above ctrl_offset_grp
    extra_offset_name = f"{suffix}_{parts[1]}_look_offset"
    if mc.objExists(extra_offset_name):
        mc.delete(extra_offset_name)

    extra_offset_grp = mc.group(empty=True, name=extra_offset_name)
    pos_ctrl_offset = mc.xform(ctrl_offset_grp, q=True, ws=True, t=True)
    rot_ctrl_offset = mc.xform(ctrl_offset_grp, q=True, ws=True, ro=True)
    mc.xform(extra_offset_grp, ws=True, t=pos_ctrl_offset, ro=rot_ctrl_offset)

    # Parent ctrl_offset_grp under extra offset group
    mc.parent(ctrl_offset_grp, extra_offset_grp)

    print(f"Created master eyelid control '{ctrl_name}', grouped eyelids in '{eyelid_grp_name}', and set up offset groups.")

def build_eye_look_control_from_guides(guide_group_name):
    # Validate guide group name ends with '_guides'
    if not guide_group_name.endswith('_guides'):
        mc.error("Guide group name must end with '_guides'")
        return
    
    # Extract suffix by removing '_guides'
    suffix = guide_group_name[:-7]  # strips last 7 chars: '_guides'
    
    # Determine color based on side (first char of suffix)
    side = suffix[0].upper()
    if side == 'L':
        ctrl_color = (0, 0, 1)  # Blue
    elif side == 'R':
        ctrl_color = (1, 0, 0)  # Red
    else:
        ctrl_color = (1, 1, 0)  # Yellow
    
    center_pivot_guide = f"{suffix}_EyeCenterPivot"
    aim_guide = f"{suffix}_Aim"
    eyelid_look_loc_name = f"{suffix}_eyelid_look_loc"
    looknull_loc_name = "LookNULL_loc"
    master_ctrl_grp = f"{suffix}_MasterControl_GRP"
    
    # Check guides exist
    if not mc.objExists(center_pivot_guide):
        mc.error(f"Guide not found: {center_pivot_guide}")
        return
    if not mc.objExists(aim_guide):
        mc.error(f"Guide not found: {aim_guide}")
        return
    
    # Get positions
    center_pos = mc.xform(center_pivot_guide, q=True, ws=True, t=True)
    aim_pos = mc.xform(aim_guide, q=True, ws=True, t=True)
    
    # Create eye joint at center pivot
    eye_joint = mc.joint(name=f"{suffix}_JNT", position=center_pos, orientation=[0,0,0])
    pupil_joint = mc.joint(name=f"{suffix}pupil_JNT", position=center_pos, orientation=[0,0,0], rad=.5)
    iris_joint = mc.joint(name=f"{suffix}iris_JNT", position=center_pos, orientation=[0,0,0], rad =.5)
    mc.parent(pupil_joint, eye_joint)
    mc.parent(iris_joint, eye_joint)

    # Create look control at aim guide
    look_ctrl_name = f"{suffix}_Look"
    look_ctrl, look_ctrl_offset = build_basic_control(
        name=look_ctrl_name,
        size=1.0,
        color_rgb=ctrl_color,
        position=aim_pos,
        rotation=(0, 0, 0)
    )
    
    # Rotate look control offset group X by 90 degrees
    mc.setAttr(f"{look_ctrl_offset}.rotateX", 90)
    
    # Create eyelid look locator at look control position
    eyelid_look_loc = mc.spaceLocator(name=eyelid_look_loc_name)[0]
    mc.xform(eyelid_look_loc, ws=True, translation=aim_pos)
    
    # Create or reference LookNULL_loc at same pos but X=0
    if mc.objExists(looknull_loc_name):
        looknull_loc = looknull_loc_name
    else:
        looknull_loc = mc.spaceLocator(name=looknull_loc_name)[0]
        pos_with_zero_x = [0, aim_pos[1], aim_pos[2]]
        mc.xform(looknull_loc, ws=True, translation=pos_with_zero_x)
    
    # Aim constraint from look control to eye joint (maintain offset)
    mc.aimConstraint(look_ctrl, eye_joint, maintainOffset=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType="scene")
    mc.pointConstraint(f'{suffix}_MasterControl_CTRL', f'{suffix}_JNT', maintainOffset=True,)
    # Parent look control offset and LookNULL_loc under eyelid look locator
    mc.parentConstraint(look_ctrl, eyelid_look_loc, maintainOffset=True)
    mc.parentConstraint(looknull_loc, eyelid_look_loc, maintainOffset=True)
    mc.setAttr(f"{suffix}_eyelid_look_loc_parentConstraint1.{suffix}_Look_CTRLW0", 0.05)
    # Aim constraint from eyelid look locator to master control group
    if mc.objExists(master_ctrl_grp):
        mc.aimConstraint(eyelid_look_loc, master_ctrl_grp, maintainOffset=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType="scene")
    else:
        print(f"Warning: Master control group '{master_ctrl_grp}' not found, skipping aimConstraint.")

def cleanup_eye_rig(guide_group_name):
    # Parse suffix from guide group name (e.g. "L_eye_guides" → "L_eye")
    parts = guide_group_name.split('_')
    if len(parts) < 2:
        mc.error(f"Invalid guide group name: {guide_group_name}")
        return
    suffix = '_'.join(parts[:2])
    
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


def build_constraints(group_name, eyelid_guide_names, control_lookup):
    """
    Sets up constraints and UV pins for eyelid controls and joints.

    Args:
        group_name (str): The name of the guide group (e.g. 'L_eye_guides').
        eyelid_guide_names (list): List of guide names for the eyelid.
        control_lookup (dict): Mapping of guide name → (control, offset group)
    """
    # Determine curve names
    upper_surface = f"{group_name}_Eyelid_Upper_CRV_loft"
    lower_surface = f"{group_name}_Eyelid_Lower_CRV_loft"
    print(upper_surface, lower_surface, group_name, eyelid_guide_names, control_lookup )
    for guide in eyelid_guide_names:
        # Derive joint and control info
        jnt_name = f'{guide}_JNT'
        ctrl, offset_grp = control_lookup.get(guide, (None, None))

        if not ctrl or not offset_grp:
            print(f"Skipping {guide} — no control found.")
            continue

        # Parent and scale constraint control to joint
        if mc.objExists(jnt_name):
            try:
                mc.parentConstraint(ctrl, jnt_name, mo=True)
                mc.scaleConstraint(ctrl, jnt_name, mo=True)
            except Exception as e:
                print(f"Constraint failed for {ctrl} to {jnt_name}: {e}")
        else:
            print(f"Joint not found: {jnt_name}")

        # Determine which loft surface to pin to
        if 'Upper' in guide:
            loft_surface = upper_surface
        elif 'Lower' in guide:
            loft_surface = lower_surface
        else:
            continue  # Skip guides that don't belong to upper/lower eyelid

        # UV Pin
        if mc.objExists(loft_surface):
            try:
                mc.select(loft_surface, offset_grp)
                mc.UVPin()
                print(f"Pinned {offset_grp} to {loft_surface}")
            except Exception as e:
                print(f"UVPin failed for {offset_grp} to {loft_surface}: {e}")
        else:
            print(f"Surface not found: {loft_surface}")
    prefix = group_name.replace("_guides", "")
    for offset in [f'{prefix}_InnerCorner_GRP', f'{prefix}_OuterCorner_GRP']:
        mc.setAttr(f'{offset}.rotateX', 90)
        mc.setAttr(f'{offset}.rotateZ', -90)

def build_eyelid_controls_and_joints(group_name):
    children = mc.listRelatives(group_name, children=True, type='transform') or []
    eyelid_guide_names = []
    def extract_info(name):
        parts = name.split('_')
        side = parts[0]
        prefix = parts[1]
        part = parts[2]
        guide_name = '_'.join(parts[3:])
        match = re.match(r"([A-Za-z]+)(\d*)", guide_name)
        if not match:
            base_name = guide_name
            number = None
        else:
            base_name = match.group(1)
            number = int(match.group(2)) if match.group(2) else None
        return side, prefix, part, base_name, number


    control_lookup = {}
    for guide in children:
        if not mc.objExists(guide):
            continue

        side, prefix, part, base_name, number = extract_info(guide)

        # Only process Eyelid guides
        if part != 'Eyelid':
            continue
        eyelid_guide_names.append(guide)
        pos = mc.xform(guide, q=True, ws=True, t=True)
        #rot = mc.xform(guide, q=True, ws=True, ro=True)
        rot = [0,0,0]
        mc.select(clear=True)
        # Create joint
        joint_name = guide.replace("guides", "JNT")
        jnt = mc.joint(name=f'{joint_name}_JNT', rad=.1)
        mc.xform(jnt, ws=True, t=pos, ro=rot)
        add_to_face_bind_set(jnt)
        # Create control
        if side == 'L':
            ctrl_color = (0, 0, 1)  # Blue for Left
        elif side == 'R':
            ctrl_color = (1, 0, 0)  # Red for Right
        else:
            ctrl_color = (1, 1, 0)  # Yellow for anything else
        ctrl_name = guide.replace("guides", "ctrl").replace("Eyelid_", "")
        build_basic_control(name=ctrl_name, size=.2, color_rgb=ctrl_color, position=pos, rotation=rot)
        
        ctrl = f'{ctrl_name}_CTRL'
        offset = f'{ctrl_name}_GRP'
        control_lookup[guide] = (ctrl, offset)

    return eyelid_guide_names, control_lookup

def skin_eyelid_majors_to_ribbons(group_name):
    # Parse side and prefix from group name
    parts = group_name.split('_')
    if len(parts) < 3:
        mc.error("Invalid group name format. Expected: side_prefix_guides")
        return

    side = parts[0]
    prefix = parts[1]

    # Construct joint names
    inner_jnt = f"{side}_{prefix}_Eyelid_InnerCorner_Major_JNT"
    outer_jnt = f"{side}_{prefix}_Eyelid_OuterCorner_Major_JNT"
    lower_jnt = f"{side}_{prefix}_Eyelid_Lower_Major_JNT"
    upper_jnt = f"{side}_{prefix}_Eyelid_Upper_Major_JNT"

    joints_upper = [inner_jnt, outer_jnt, upper_jnt]
    joints_lower = [inner_jnt, outer_jnt, lower_jnt]

    # Loft surface names
    upper_loft = f"{group_name}_Eyelid_Upper_CRV_loft"
    lower_loft = f"{group_name}_Eyelid_Lower_CRV_loft"

    # Skin upper loft
    if all(mc.objExists(jnt) for jnt in joints_upper) and mc.objExists(upper_loft):
        mc.skinCluster(joints_upper, upper_loft, toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1)
        print(f"Skinned upper loft to: {joints_upper}")
    else:
        print(f"Skipping upper loft skinning — missing joints or surface.")

    # Skin lower loft
    if all(mc.objExists(jnt) for jnt in joints_lower) and mc.objExists(lower_loft):
        mc.skinCluster(joints_lower, lower_loft, toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1)
        print(f"Skinned lower loft to: {joints_lower}")
    else:
        print(f"Skipping lower loft skinning — missing joints or surface.")

def build_blink_system(group_name):
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

        ctrl_color = (0, 0, 1) if side == 'L' else (1, 0, 0) if side == 'R' else (1, 1, 0)
        ctrl_temp = guide.replace('guides', 'ctrl').replace('Eyelid_', '')
        ctrl_name = f'{ctrl_temp}_Major'
        ctrl, offset = build_basic_control(ctrl_name, size=0.4, color_rgb=ctrl_color, position=pos, rotation=(0, 0, 0))

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
    mc.parentConstraint(f"{side}_{prefix}_OuterCorner_Major_CTRL", f"{side}_{prefix}_OuterCorner_CTRL" )
    mc.parentConstraint(f"{side}_{prefix}_InnerCorner_Major_CTRL", f"{side}_{prefix}_InnerCorner_CTRL" )

def build_eye_curves_from_guides(group_name):
    children = mc.listRelatives(group_name, children=True, type='transform') or []
    
    # Parse guide names by part, type, side and number
    # Expected format: {side}_{prefix}_{part}_{guideName}[number]
    # Example: L_eye_Eyelid_InnerUpper01
    
    def extract_info(name):
        parts = name.split('_')
        side = parts[0]
        prefix = parts[1]
        part = parts[2]
        guide_name = '_'.join(parts[3:])
        match = re.match(r"([A-Za-z]+)(\d*)", guide_name)
        if not match:
            base_name = guide_name
            number = None
        else:
            base_name = match.group(1)
            number = int(match.group(2)) if match.group(2) else None
        return side, prefix, part, base_name, number
    
    # Organize guides in a dictionary: guides[part][base_name] = sorted list of guides
    guides = {}
    for child in children:
        side, prefix, part, base_name, number = extract_info(child)
        if part not in guides:
            guides[part] = {}
        if base_name not in guides[part]:
            guides[part][base_name] = []
        guides[part][base_name].append((child, number))
    
    # Sort each list by number (None goes first)
    for part in guides:
        for base_name in guides[part]:
            guides[part][base_name].sort(key=lambda x: x[1] if x[1] is not None else 0)
    
    curve_names = []
    
    def build_curve_for_part(part):
        if part not in guides:
            print(f"No guides found for part '{part}'")
            return
        
        g = guides[part]
        
        # Build upper curve list following your pattern:
        # InnerCorner → InnerUpper* → Upper → OuterUpper* → OuterCorner
        upper_points = []
        # Lower curve: OuterCorner → OuterLower* → Lower → InnerLower* → InnerCorner
        lower_points = []
        
        # Helper to add guide names safely
        def add_guides(base_name, forward=True):
            if base_name in g:
                if forward:
                    return [x[0] for x in g[base_name]]
                else:
                    return [x[0] for x in reversed(g[base_name])]
            return []
        
        # Build upper curve
        upper_points += add_guides('InnerCorner')
        upper_points += add_guides('InnerUpper')
        upper_points += add_guides('Upper')
        upper_points += add_guides('OuterUpper')
        upper_points += add_guides('OuterCorner')
        
        # Build lower curve
        lower_points += add_guides('OuterCorner', forward=False)
        lower_points += add_guides('OuterLower', forward=False)
        lower_points += add_guides('Lower', forward=False)
        lower_points += add_guides('InnerLower', forward=False)
        lower_points += add_guides('InnerCorner', forward=False)
        
        # Remove duplicates but keep order
        def unique_order(seq):
            seen = set()
            return [x for x in seq if not (x in seen or seen.add(x))]

        upper_points = unique_order(upper_points)
        lower_points = unique_order(lower_points)

        points_upper = [mc.xform(p, q=True, ws=True, t=True) for p in upper_points]
        points_lower = [mc.xform(p, q=True, ws=True, t=True) for p in lower_points]


        degree = 3
        
        if len(points_upper) >= 4:
            mc.curve(name=f"{group_name}_{part}_Upper_CRV", degree=degree, point=points_upper)
            print(f"Built smooth upper curve for {part}")
                        
        elif len(points_upper) >= 2:
            mc.curve(name=f"{group_name}_{part}_Upper_CRV", degree=1, point=points_upper)
            print(f"Built linear upper curve for {part} (not enough points for smooth)")

        if len(points_lower) >= 4:
            mc.curve(name=f"{group_name}_{part}_Lower_CRV", degree=degree, point=points_lower)
            print(f"Built smooth lower curve for {part}")
        elif len(points_lower) >= 2:
            mc.curve(name=f"{group_name}_{part}_Lower_CRV", degree=1, point=points_lower)
            print(f"Built linear lower curve for {part} (not enough points for smooth)")
    
    # Build curves for Socket and Eyelid
    #build_curve_for_part('Socket')
    build_curve_for_part('Eyelid')
    print(base_name)
    curve_names = [f'{group_name}_Eyelid_Upper_CRV', f'{group_name}_Eyelid_Lower_CRV']
    # f'{prefix}_guides_Socket_Upper_CRV'
    lofts = make_loft(curve_names, offset=0.1)
'''
# Example usage
check_eye_guides("L_eye_guides")
build_eye_curves_from_guides('L_eye_guides')
#build_eyelid_controls_and_joints("L_eye_guides")

eyelid_guides, ctrl_map = build_eyelid_controls_and_joints("L_eye_guides")
build_constraints("L_eye_guides", eyelid_guides, ctrl_map)
build_blink_system("L_eye_guides")
skin_eyelid_majors_to_ribbons("L_eye_guides")
build_socket_controls_and_joints("L_eye_guides")
create_master_eyelid_control_and_group("L_eye_guides")
build_eye_look_control_from_guides("L_eye_guides")
cleanup_eye_rig("L_eye_guides")
'''

def build_eye(groupname):
    check_eye_guides(groupname)
    build_eye_curves_from_guides(groupname)
    eyelid_guides, ctrl_map = build_eyelid_controls_and_joints(groupname)
    build_constraints(groupname, eyelid_guides, ctrl_map)
    build_blink_system(groupname)
    skin_eyelid_majors_to_ribbons(groupname)
    build_socket_controls_and_joints(groupname)
    create_master_eyelid_control_and_group(groupname)
    build_eye_look_control_from_guides(groupname)
    cleanup_eye_rig(groupname)

build_eye("L_eye_guides")
build_eye("R_eye_guides")