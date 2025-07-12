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


def Build_Nose(guide_group):
    # === Step 1: Get Suffix and Setup ===
    suffix = get_suffix_from_group(guide_group)  # e.g., "Nose"
    
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
        Simple_joint_and_Control(
            guide=f'{suffix}_{base}',
            suffix=suffix,
            check_side=True,
            CTRL_Size=.5,
            JNT_Size=0.5
        )

    # === Step 3: Build Nose Master Control at M_NoseBridge ===
    bridge_guide = f'{suffix}_M_NoseBridge'
    master_pos = mc.xform(bridge_guide, q=True, ws=True, t=True)
    Nose_Master_CTRL, Nose_Master_GRP = build_basic_control(
        name=f'{suffix}_Master',
        size=1.5,
        color_rgb=(1, 0.6, 0),  # Orangey Yellow
        position=master_pos,
        rotation=(0, 0, 0)
    )

    # === Step 4: Build Nose Root Control/Joint ===
    Simple_joint_and_Control(
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
    mc.parent(f'{suffix}_L_Nostril_Outer_GRP', f'{suffix}_L_Nostril_CTRL')
    mc.parent(f'{suffix}_R_Nostril_Outer_GRP', f'{suffix}_R_Nostril_CTRL')
    for guide in ['L_Nostril', 'R_Nostril', 'M_Nostril_Inner', 'M_Tip']:
        mc.parent(f'{suffix}_{guide}_GRP', f'{suffix}_M_NoseRoot_CTRL')
    for guide in ['M_NoseRoot', 'R_UpperCorner', 'L_UpperCorner', 'M_NoseBridge']:
        mc.parent(f'{suffix}_{guide}_GRP', f'{suffix}_Master_CTRL')

    print(f"✅ Built nose module for group: {guide_group} (suffix: {suffix})")











Build_Nose("Nose_guides")









'''nose_basenames = [
    'M_Tip', 'L_Nostril', 'M_NoseRoot', 'L_Nostril_Outer',
    'M_NoseBridge', 'M_Nostril_Inner', 'L_UpperCorner',
    'R_Nostril', 'R_Nostril_Outer', 'R_UpperCorner'
]

check_guides("Nose_guides", part="Nose", guide_basenames=nose_basenames)
Simple_joint_and_Control(
    guide = 'Nose_M_NoseBridge',
    suffix='Nose',
    orient=True,
    overwrite=False,
    overwrite_name=None,
    scale=True,
    check_side=False,
    CTRL_Color=(0, 0, 1),  # Default blue
    CTRL_Size=0.2,
    JNT_Size=0.5
)
'''