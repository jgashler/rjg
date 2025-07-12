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
    JNT_Size=0.5
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
    add_to_face_bind_set(jnt)
    mc.xform(jnt, ws=True, t=pos, ro=rot)
    mc.setAttr(f"{jnt}.radius", JNT_Size)

    # Create control
    ctrl, ctrl_offset = build_basic_control(
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
        jnt_name = f"{guide}_JNT"
        ctrl_name = f"{guide}_CTRL"
        grp_name = f"{guide}_GRP"

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

def get_suffix_from_group(group_name):
    """
    Extracts the suffix from the guide group name (e.g. 'Nose_guides' -> 'Nose').

    Args:
        group_name (str): The name of the guide group.

    Returns:
        str: The suffix (e.g. 'Nose').
    """
    if not group_name.endswith('_guides'):
        raise ValueError(f"Group name '{group_name}' must end with '_guides'")
    
    return group_name.rsplit('_guides', 1)[0]

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

def check_feather_chains(prefix, guide_list):
    """
    Validates that each wing arm has at least one feather chain and
    that every feather chain contains exactly 4 joints in sequence.
    
    Args:
        prefix (str): The prefix like 'L_wing'.
        guide_list (list): List of all guides under the guide group.
    """
    pattern = re.compile(rf'{prefix}_arm(?P<arm>\d+)_feather(?P<feather>\d+)_(?P<seg>\d+)$')

    # Collect feather chains by arm and feather
    feather_dict = {}
    for guide in guide_list:
        match = pattern.match(guide)
        if not match:
            continue

        arm = match.group('arm')
        feather = match.group('feather')
        seg = match.group('seg')

        arm_key = f'arm{arm}'
        feather_key = f'feather{feather}'

        feather_dict.setdefault(arm_key, {}).setdefault(feather_key, []).append((int(seg), guide))

    # Validate each arm
    for arm in ['arm01', 'arm02', 'arm03']:
        if arm not in feather_dict:
            raise RuntimeError(f"[ERROR] Missing feather chains for {arm}")

        feathers = feather_dict[arm]
        for feather_name, segments in feathers.items():
            if len(segments) != 4:
                raise RuntimeError(f"[ERROR] {arm} -> {feather_name} has {len(segments)} segments, expected 4.")
            
            # Ensure segments are labeled correctly (01–04)
            segments_sorted = sorted(segments, key=lambda x: x[0])
            expected = [1, 2, 3, 4]
            actual = [s[0] for s in segments_sorted]
            if actual != expected:
                raise RuntimeError(f"[ERROR] {arm} -> {feather_name} has incorrect segment order: {actual} (expected {expected})")

    print("[INFO] Feather chains validated successfully.")

def build_wing(group_name):
    prefix = get_suffix_from_group(group_name)

    # --- Non-feather base guide check ---
    base_guides = [
        f'scapula',
        f'arm01',
        f'arm02',
        f'arm03'
    ]
    check_guides(group_name, prefix, base_guides)

    # --- Feather guide check ---
    feather_guides = mc.listRelatives(group_name, allDescendents=True, type='transform') or []
    check_feather_chains(prefix, feather_guides)
    arm = [f'{prefix}_scapula', f'{prefix}_arm01', f'{prefix}_arm02',f'{prefix}_arm03']
    for guide in arm: 
        Simple_joint_and_Control(guide,suffix=None,orient=True,scale=True,check_side=True,CTRL_Size=2,JNT_Size=1)
    chain_parts(arm, jnt_parent=None, ctrl_parent=None)
    
    guide_list = mc.listRelatives(group_name, allDescendents=True, type='transform') or []

    # Regex pattern to detect feathers (e.g., L_wing_arm01_feather01_03)
    pattern = re.compile(rf'{prefix}_arm(?P<arm>\d+)_feather(?P<feather>\d+)_\d+')

    # Build structure: { arm01: { feather01: set([...]) } }
    arm_chains = {}

    for guide in guide_list:
        match = pattern.match(guide)
        if not match:
            continue
        arm = f"arm{match.group('arm')}"
        feather = f"feather{match.group('feather')}"
        arm_chains.setdefault(arm, {}).setdefault(feather, set()).add(guide)

    # Go through each arm and feather
    for arm, feathers in sorted(arm_chains.items()):
        for feather, guide_set in sorted(feathers.items()):
            # Sort guides in order by trailing number (_01, _02, _03, _04)
            sorted_guides = sorted(
                list(guide_set),
                key=lambda name: int(name.split('_')[-1])
            )

            # Create joints and controls at each guide
            for guide in sorted_guides:
                Simple_joint_and_Control(
                    guide,
                    suffix=None,
                    orient=True,
                    overwrite=False,
                    scale=True,
                    check_side=True,
                    CTRL_Color=(1, 1, 0),  # optional
                    CTRL_Size=.5,
                    JNT_Size=1
                )

            # Chain the joints and/or controls
            chain_parts(
                chain_names=sorted_guides,
                jnt_parent=f'{prefix}_{arm}_JNT',
                ctrl_parent=f'{prefix}_{arm}_CTRL',
                joints=True,
                controls=True
            )




build_wing('wing_L_guides')