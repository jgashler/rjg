import maya.cmds as mc
import math
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
    prefix=None,
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
        prefix (str or None): Suffix to prepend (e.g. 'Nose'). If None, no prefix added.
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
        if prefix:
            # If prefix is part of the guide name, remove it from base_name
            prefix = f"{prefix}_"
            if base_name.startswith(prefix):
                base_name = base_name[len(prefix):]

    # Build final names
    if prefix:
        joint_name = f"{prefix}_{base_name}_JNT"
        ctrl_name = f"{prefix}_{base_name}"
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

def strip_prefix_from_guide(prefix, guide_name):
    """
    Removes the prefix (and underscore) from the start of a guide name,
    and strips the leading underscore from the result (if any).

    Args:
        prefix (str): The prefix/prefix used (e.g. 'Nose').
        guide_name (str): The full guide name (e.g. 'Nose_M_Tip').

    Returns:
        str: The base guide name without the prefix (e.g. 'M_Tip').
    """
    prefix = f"{prefix}_"
    if guide_name.startswith(prefix):
        result = guide_name[len(prefix):]
        return result.lstrip('_')
    return guide_name

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

    prefix = group_name.replace('_guides', '')  # use this as the prefix

    # Build expected guide names
    expected_guides = [f"{prefix}_{name}" for name in guide_basenames]

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

def build_ik_spline_with_controls(aim_joints=None, prefix=None, sub=False, FeatherType=None):
    # Step 1: Create IK spline
    ik_handle, effector, curve = mc.ikHandle(
        sj=aim_joints[0],
        ee=aim_joints[-1],
        sol='ikSplineSolver',
        ccv=True,
        pcv=False
    )
    curve = mc.rename(curve, f'{prefix}_{FeatherType}_curve')
    ik_handle = mc.rename(ik_handle, f'{prefix}_{FeatherType}_ik_handle')
    mc.parent(ik_handle, f'{prefix}_handle_grp')
    mc.parent(curve, f'{prefix}_handle_grp')
    # Step 2: For each CV on the curve, create cluster + control
    cvs = mc.ls(f"{curve}.cv[*]", fl=True)
    
    for i, cv in enumerate(cvs, start=1):
        # Make cluster for the CV
        cluster, cluster_handle = mc.cluster(cv, n=f"{prefix}_{FeatherType}Feather_aimCluster_{i:02}")
        mc.parent(cluster_handle, f'{prefix}_handle_grp')
        # Get cluster position
        pos = mc.pointPosition(cv, w=True)
        if sub == False:
            # Make control
            ctrl_name = f"{prefix}_Main_Feather_aim_{i:02}"
            ctrl, offset = build_basic_control(
                name=ctrl_name,
                shape='circle',
                size=1.0,
                color_rgb=(1, 1, 0),
                position=pos,
                rotation=(0, 0, 0)
            )
        
            # Parent cluster to control
            mc.parentConstraint(ctrl, cluster_handle,)

            close_offset = mc.group(empty=True, name=f'{prefix}Aim_{i:02}_ArmClose_offset')
            mc.xform(close_offset, ws=True, t=pos,)
            mc.parent(close_offset, offset)
            mc.parent(ctrl, close_offset)

        else:
            mc.parentConstraint(f"{prefix}_Main_Feather_aim_{i:02}_CTRL", cluster_handle,)
    
    return ik_handle, curve


def build_curve(guide_list, prefix, degree=3):
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

def look_at_rotation(pos1, pos2):
    """
    Returns rotation (rx, ry, rz) in degrees so Z+ points from pos1 to pos2.
    """
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    dz = pos2[2] - pos1[2]

    # Yaw (rotation around Y axis)
    ry = math.degrees(math.atan2(dx, dz))  # note order: x/z

    # Pitch (rotation around X axis)
    dist_xz = math.sqrt(dx*dx + dz*dz)
    rx = -math.degrees(math.atan2(dy, dist_xz))

    # Roll is 0 if you don't care
    rz = 0

    return (rx, ry, rz)

def count_feather_guides(prefix, feather):
    count = 0
    guides = []
    
    # We'll just loop up to some reasonable high number to check
    for i in range(1, 200):  
        num_str = f"{i:02}" if i < 10 else str(i)  # pad with zero if < 10
        name = f"{prefix}_{feather}_{num_str}_guide"
        
        if mc.objExists(name):
            guides.append(name)
            count += 1
    
    print(f"Found {count} feather guide(s): {guides}")
    return count, guides

def place_joints_on_guide_curve(guides, feather_count, prefix, feathertype, up_controls=False):
    # Get world positions from guides
    positions = [mc.xform(g, q=True, ws=True, t=True) for g in guides]
    
    # Build temp curve from guide positions
    curve = mc.curve(p=positions, degree=3)  # cubic curve
    mc.rebuildCurve(curve, ch=False, rpo=True, spans=len(positions)-1, degree=3)
    
    joints = []
    upgrps = []
    upctrs = []
    for i in range(feather_count):
        u = float(i) / (feather_count - 1) if feather_count > 1 else 0.0
        pos = mc.pointOnCurve(curve, pr=u, p=True) #Wing_L_MainFeather01_guide Wing_L_MainFeather_01_guide
        pos2 = mc.xform(f'{prefix}_{feathertype}Feather_{i+1:02}_guide', q=True, ws=True, t=True)
        tangent = look_at_rotation(pos,pos2)
        
        jnt = mc.joint(p=pos, name=f"{prefix}_{feathertype}FeatherAim_{i+1:02}_jnt")
        joints.append(jnt)
        if up_controls == True:
            rot = mc.xform(jnt, q=True, ws=False, rotation=True)
            size = .2 if feathertype != "Main" else .5
            upctr, upgrp = build_basic_control(name=f'{prefix}_{feathertype}AimUp{i+1:02}', shape='circle', size=size, color_rgb=(1, 1, 0), position=pos, rotation=tangent)
            mc.parentConstraint(jnt, upgrp, mo=True)
            upgrps.append(upgrp)
            upctrs.append(upctr)
            mc.parent(upgrp, f'{prefix}_upAim_grp')
            mc.select(jnt)

    # Delete temp curve
    mc.delete(curve)
    mc.parent(f"{prefix}_{feathertype}FeatherAim_01_jnt", f'{prefix}_feather_grp')
    return joints, upgrps, upctrs


def get_sub_groups(prefix):
    """
    Returns a sorted list of sub-groups under the {prefix}_guides group,
    stripped of the prefix.
    """
    group_name = f"{prefix}_guides"
    if not mc.objExists(group_name):
        print(f"[WARN] Group '{group_name}' does not exist.")
        return []

    # List children of the group
    children = mc.listRelatives(group_name, children=True, fullPath=False) or []

    # Filter for sub-groups
    sub_groups = [c for c in children if c.startswith(f"{prefix}_Sub")]

    # Sort numerically
    sub_groups.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))

    # Strip prefix
    stripped_sub_groups = [name.replace(f"{prefix}_", "", 1) for name in sub_groups]

    return stripped_sub_groups


def build_sub_feathers(prefix=None, sub=None, main_surf=None,):
    subcount, subguides = count_feather_guides(prefix = prefix, feather=f'{sub}Feather')
    print(subcount, subguides, sub)
    sub_aimjnt_list = []
    aim_joints, upgrps, upctrs = place_joints_on_guide_curve([f'{prefix}_WingAim_01_guide', f'{prefix}_WingAim_02_guide', f'{prefix}_WingAim_03_guide', f'{prefix}_WingAim_04_guide'], subcount, prefix, sub, up_controls=True ) 
    sub_aimjnt_list.extend(aim_joints)
    build_ik_spline_with_controls(aim_joints=aim_joints, prefix=prefix, sub=True, FeatherType=sub)
    rot_offset_list = []
    base_offsets = []
    for guide in subguides:
        num = guide.split("_")[-2]
        ee_guide = f'{prefix}_{sub}Feather_{num}_ee_guide'
        basepos = mc.xform(guide, q=True, ws=True, t=True)
        eepos = mc.xform(ee_guide, q=True, ws=True, t=True)
        midpos = [basepos[i] + (eepos[i] - basepos[i]) * .5 for i in range(3)]
        rot = mc.xform(guide, q=True, ws=True, ro=True)
        mid_guide = mc.spaceLocator(p=midpos, name=f"interp_locator{guide}")[0]
        mc.xform(mid_guide, ws=True, ro=rot, t=midpos)
        basejnt, basectrl, basectrl_offset =Simple_joint_and_Control(
            guide,
            prefix=None,
            orient=True,
            overwrite=True,
            overwrite_name=f'{prefix}{sub}Feather_{num}_base',
            scale=True,
            check_side=True,
            CTRL_Size=0.2,
            JNT_Size=0.5
        )
        midjnt, midctrl, midctrl_offset =Simple_joint_and_Control(
            mid_guide,
            prefix=None,
            orient=True,
            overwrite=True,
            overwrite_name=f'{prefix}{sub}Feather_{num}_mid',
            scale=True,
            check_side=True,
            CTRL_Size=0.2,
            JNT_Size=0.5
        )
        eejnt, eectrl, eectrl_offset =Simple_joint_and_Control(
            ee_guide,
            prefix=None,
            orient=True,
            overwrite=True,
            overwrite_name=f'{prefix}{sub}Feather_{num}_ee',
            scale=True,
            check_side=True,
            CTRL_Size=0.2,
            JNT_Size=0.5
        )
        pre_jnt = None
        for part in [guide, mid_guide, ee_guide]:
            if part == guide: 
                trans = basepos
                nameing = 'base'
                offset = basectrl_offset
                ctrl = basectrl
                jnt = basejnt
            elif part == mid_guide:
                trans = midpos
                nameing = 'mid'
                offset = midctrl_offset
                ctrl = midctrl
                jnt = midjnt
            else:
                trans = eepos 
                nameing = 'ee'
                offset = eectrl_offset
                ctrl = eectrl
                jnt = eejnt
            rot_offset = mc.group(empty=True, name=f'{prefix}_{sub}Feather_{num}_{nameing}_rotOffset')
            mc.xform(rot_offset, ws=True, t=trans, ro=rot)
            mc.parent(rot_offset, offset)
            mc.parent(ctrl, rot_offset)
            rot_offset_list.append(rot_offset)
            if pre_jnt != None:
                mc.parent(jnt, pre_jnt)
                mc.parent(offset, pre_ctrl)
                pre_jnt = jnt
                pre_ctrl = ctrl
            else:
                pre_jnt = jnt
                pre_ctrl = ctrl
                mc.parent(jnt, f'{prefix}_root_jnt')
                mc.parent(offset, f'{prefix}_feather_grp')
        base_offsets.append(basectrl_offset)
        mc.delete(mid_guide)
        mc.skinCluster(eejnt, midjnt, basejnt, f'{prefix}_{sub}Feather_{num}_GEO', tsb=True )
        
        mc.select(clear=True)
        mc.select(main_surf[0])
        mc.select(basectrl_offset, add=True)
        print(main_surf)
        mc.UVPin()
        for attr in ["rotateX", "rotateY", "rotateZ"]:
            # Find any nodes driving this attribute
            connections = mc.listConnections(f"{basectrl_offset}.{attr}", s=True, d=False, plugs=True)
            if connections:
                for conn in connections:
                    mc.disconnectAttr(conn, f"{basectrl_offset}.{attr}")
        mc.aimConstraint(
            f'{prefix}_{sub}FeatherAim_{num}_jnt',
            basectrl_offset,
            aimVector=(0, 1, 0),
            upVector=(1, 0, 0),
            mo=False,
            weight=1.0,
            worldUpType="objectrotation", worldUpObject =f'{prefix}_{sub}AimUp{num}_CTRL'
            #worldUpVector = (1,0,0),
            #worldUpType = 'None'
        )
    return rot_offset_list, base_offsets, sub_aimjnt_list




def build_wing(group='Wing_L_guides'):
    prefix = get_prefix_from_group(group)

    feather_grp = mc.group(em=True, name=f'{prefix}_feather_grp')
    handle_grp = mc.group(em=True, name=f'{prefix}_handle_grp')
    upAim_grp = mc.group(em=True, name=f'{prefix}_upAim_grp')
    mc.select(clear=True)
    root_joint = mc.joint(name=f'{prefix}_root_jnt')
    fk_group = mc.group(em=True, name=f'{prefix}_FK_grp')
    ik_group = mc.group(em=True, name=f'{prefix}_IK_grp')

    maincount, mainguides = count_feather_guides(prefix = prefix, feather='MainFeather')
    curve_offset = 1
    main_curve = build_curve(mainguides, prefix)
    main_curve2 = mc.duplicate(main_curve)
    mc.move(0, 0,curve_offset, main_curve, r=True)
    mc.move(0, 0,-curve_offset, main_curve2, r=True)
    main_surf = mc.loft(main_curve, main_curve2, name=f'{prefix}_Main_loft')
    full_aimjnt_list = []
    aim_joints, upgrps, upctrs = place_joints_on_guide_curve([f'{prefix}_WingAim_01_guide', f'{prefix}_WingAim_02_guide', f'{prefix}_WingAim_03_guide', f'{prefix}_WingAim_04_guide'], maincount, prefix, 'Main', up_controls=True) 
    full_aimjnt_list.extend(aim_joints)
    build_ik_spline_with_controls(aim_joints=aim_joints, prefix=prefix, sub=False, FeatherType='Main')

    rot_offset_list = []
    base_offsets = []
    for guide in mainguides:
        num = guide.split("_")[-2]
        ee_guide = f'{prefix}_MainFeather_{num}_ee_guide'
        basepos = mc.xform(guide, q=True, ws=True, t=True)
        eepos = mc.xform(ee_guide, q=True, ws=True, t=True)
        midpos = [basepos[i] + (eepos[i] - basepos[i]) * .5 for i in range(3)]
        rot = mc.xform(guide, q=True, ws=True, ro=True)
        mid_guide = mc.spaceLocator(p=midpos, name=f"interp_locator{guide}")[0]
        mc.xform(mid_guide, ws=True, ro=rot, t=midpos)
        basejnt, basectrl, basectrl_offset =Simple_joint_and_Control(
            guide,
            prefix=None,
            orient=True,
            overwrite=True,
            overwrite_name=f'{prefix}MainFeather_{num}_base',
            scale=True,
            check_side=True,
            CTRL_Size=0.2,
            JNT_Size=0.5
        )
        midjnt, midctrl, midctrl_offset =Simple_joint_and_Control(
            mid_guide,
            prefix=None,
            orient=True,
            overwrite=True,
            overwrite_name=f'{prefix}MainFeather_{num}_mid',
            scale=True,
            check_side=True,
            CTRL_Size=0.2,
            JNT_Size=0.5
        )
        eejnt, eectrl, eectrl_offset =Simple_joint_and_Control(
            ee_guide,
            prefix=None,
            orient=True,
            overwrite=True,
            overwrite_name=f'{prefix}MainFeather_{num}_ee',
            scale=True,
            check_side=True,
            CTRL_Size=0.2,
            JNT_Size=0.5
        )
        pre_jnt = None
        for part in [guide, mid_guide, ee_guide]:
            if part == guide: 
                trans = basepos
                nameing = 'base'
                offset = basectrl_offset
                ctrl = basectrl
                jnt = basejnt
            elif part == mid_guide:
                trans = midpos
                nameing = 'mid'
                offset = midctrl_offset
                ctrl = midctrl
                jnt = midjnt
            else:
                trans = eepos 
                nameing = 'ee'
                offset = eectrl_offset
                ctrl = eectrl
                jnt = eejnt
            rot_offset = mc.group(empty=True, name=f'{prefix}_MainFeather_{num}_{nameing}_rotOffset')
            mc.xform(rot_offset, ws=True, t=trans, ro=rot)
            mc.parent(rot_offset, offset)
            mc.parent(ctrl, rot_offset)
            rot_offset_list.append(rot_offset)
            if pre_jnt != None:
                mc.parent(jnt, pre_jnt)
                mc.parent(offset, pre_ctrl)
                pre_jnt = jnt
                pre_ctrl = ctrl
            else:
                pre_jnt = jnt
                pre_ctrl = ctrl
                mc.parent(jnt,root_joint)
                mc.parent(offset,feather_grp)
        base_offsets.append(basectrl_offset)
        mc.delete(mid_guide)
        mc.skinCluster(eejnt, midjnt, basejnt, f'{prefix}_MainFeather_{num}_GEO', tsb=True)
        
        mc.select(clear=True)
        mc.select(main_surf[0])
        mc.select(basectrl_offset, add=True)
        print(main_surf)
        mc.UVPin()
        for attr in ["rotateX", "rotateY", "rotateZ"]:
            # Find any nodes driving this attribute
            connections = mc.listConnections(f"{basectrl_offset}.{attr}", s=True, d=False, plugs=True)
            if connections:
                for conn in connections:
                    mc.disconnectAttr(conn, f"{basectrl_offset}.{attr}")
        mc.aimConstraint(
            f'{prefix}_MainFeatherAim_{num}_jnt',
            basectrl_offset,
            aimVector=(0, 1, 0),
            upVector=(1, 0, 0),
            mo=False,
            weight=1.0,
            #worldUpVector = (1,0,0),
            worldUpType="objectrotation", worldUpObject =f'{prefix}_MainAimUp{num}_CTRL'
            #worldUpType = 'None'
        )

    sub_groups = get_sub_groups(prefix)
    print(sub_groups)
    for sub in sub_groups:
        subrot_offset_list, subbase_offsets, sub_aimjnt_list =build_sub_feathers(prefix, sub, main_surf,)
        rot_offset_list.extend(subrot_offset_list)
        full_aimjnt_list.extend(sub_aimjnt_list)

    pre_jnt = None
    pre_ctrl = None
    armjnts = []
    armoffsets = []
    armctrls = []
    armcloses= []

    #arm Logic
    FKIKSwitch_pos = mc.xform(f'{prefix}_Close', q=True, ws=True, t=True)
    FKIKSwitch_CTL, FKIKSwitch_GRP = build_basic_control(name=f'{prefix}_FKIKSwitch', shape='circle', size=5.0, color_rgb=(1, 1, 0), position=FKIKSwitch_pos, rotation=(0, 0, 0))
    mc.addAttr(FKIKSwitch_CTL, longName="FK_IK", attributeType="bool", keyable=True)
    rev_node = mc.createNode("reverse", name=f"{prefix}IKReverse")
    mc.connectAttr(f'{FKIKSwitch_CTL}.FK_IK', f'{rev_node}.inputX')


    #bind
    bind_joints = []
    pre_jnt = None
    for obj in [f'{prefix}_01_guide', f'{prefix}_02_guide', f'{prefix}_03_guide', f'{prefix}_04_guide']:
        # Get the base name and generate joint name
        base_name = obj.split('|')[-1].replace('_guide', '')
        joint_name = f"{base_name}_bind_jnt"

        # Clear selection before creating the joint to avoid parenting
        mc.select(clear=True)
        joint = mc.joint(name=joint_name)
        bind_joints.append(joint)

        # Match translation and rotation in world space
        pos = mc.xform(obj, q=True, ws=True, t=True)
        rot = mc.xform(obj, q=True, ws=True, ro=True)
        mc.xform(joint, ws=True, t=pos)
        mc.xform(joint, ws=True, ro=rot)
        if pre_jnt != None:
            mc.parent(joint_name, pre_jnt)
        pre_jnt = joint_name
    mc.skinCluster(bind_joints, main_surf)
    pre_jnt = None


    #fk
    for guide in [f'{prefix}_01_guide', f'{prefix}_02_guide', f'{prefix}_03_guide', f'{prefix}_04_guide']:
        parts = guide.split("_")  # ["wing", "l", "01", "guide"]
        number = parts[-2]        # second to last = "01", "02", etc.
        print(number)
        jnt, ctrl, ctrl_offset = Simple_joint_and_Control(
            guide,
            prefix=None,
            orient=True,
            overwrite=True,
            overwrite_name=f'{prefix}_{number}_FK',
            scale=True,
            check_side=False,
            CTRL_Color=(0, 0, 1),
            CTRL_Size=0.5,
            JNT_Size=0.5,
            #bind=False
        )
        rot = mc.xform(guide, q=True, ws=True, ro=True)
        trans = mc.xform(guide, q=True, ws=True, t=True)
        close_offset = mc.group(empty=True, name=f'{prefix}_{number}_FK_ArmClose_offset')
        mc.xform(close_offset, ws=True, t=trans, ro=rot)
        mc.parent(close_offset, ctrl_offset)
        mc.parent(ctrl, close_offset)
        if pre_jnt != None:
            mc.parent(jnt, pre_jnt)
            mc.parent(ctrl_offset, pre_ctrl)
            pre_jnt = jnt
            pre_ctrl = ctrl
        else:
            pre_jnt = jnt
            pre_ctrl = ctrl
        armjnts.append(jnt)
        armoffsets.append(ctrl_offset)
        armctrls.append(ctrl)
        armcloses.append(close_offset)
    for num in ['01', '02', '03', '04']:
        if num != '01':
            mc.parentConstraint(f'{prefix}_{num}_bind_jnt', f'{prefix}_Main_Feather_aim_{num}_GRP', mo=True)
        mc.parentConstraint(f'{prefix}_{num}_FK_JNT', f'{prefix}_{num}_bind_jnt' )
    for cont in [f'{prefix}_Close', f'{prefix}_FeatherShaper', f'{prefix}_Span']:
        rot = mc.xform(cont, q=True, ws=True, ro=True)
        trans = mc.xform(cont, q=True, ws=True, t=True)
        build_basic_control(name=f'{cont}', shape='circle', size=2.0, position=trans, rotation=rot)
    mc.parent(f'{prefix}_FeatherShaper_GRP', f'{prefix}_Span_CTRL')
    mc.parent(f'{prefix}_Span_GRP', f'{prefix}_04_FK_CTRL')

    #ik
    IK_joints = []
    pre_jnt = None
    for obj in [f'{prefix}_01_guide', f'{prefix}_02_guide', f'{prefix}_03_guide', f'{prefix}_04_guide']:
        # Get the base name and generate joint name
        base_name = obj.split('|')[-1].replace('_guide', '')
        joint_name = f"{base_name}_IK_jnt"

        # Clear selection before creating the joint to avoid parenting
        mc.select(clear=True)
        joint = mc.joint(name=joint_name)
        IK_joints.append(joint)

        # Match translation and rotation in world space
        pos = mc.xform(obj, q=True, ws=True, t=True)
        rot = mc.xform(obj, q=True, ws=True, ro=True)
        mc.xform(joint, ws=True, t=pos)
        mc.xform(joint, ws=True, ro=rot)
        if pre_jnt != None:
            mc.parent(joint_name, pre_jnt)
        pre_jnt = joint_name

    pv_pos = mc.xform(f'{prefix}_IK_Aim', q=True, ws=True, t=True)
    ikaimCTL, ikaimGRP = build_basic_control(name=f'{prefix}_IK_Aim', shape='circle', size=5.0, color_rgb=(1, 1, 0), position=pv_pos, rotation=(0, 0, 0))
    
    ikhandel  = mc.ikHandle(
        name=f"{prefix}_ikHandle",
        sj=f"{prefix}_01_IK_jnt", 
        ee=f"{prefix}_03_IK_jnt", 
        sol="ikRPsolver"
    )[0]
    #print(ikhandel)

    mc.poleVectorConstraint(ikaimCTL, ikhandel)
    IK_Root_pos = mc.xform(f'{prefix}_01_guide', q=True, ws=True, t=True)
    IK_Root_CTL, IK_Root_GRP = build_basic_control(name=f'{prefix}_IK_Root', shape='circle', size=5.0, color_rgb=(1, 1, 0), position=IK_Root_pos, rotation=(0, 0, 0))
    mc.parentConstraint(IK_Root_CTL, f"{prefix}_01_IK_jnt")

    IK_EE_pos = mc.xform(f'{prefix}_03_guide', q=True, ws=True, t=True)
    IK_EE_CTL, IK_EE_GRP = build_basic_control(name=f'{prefix}_IK_EE', shape='circle', size=5.0, color_rgb=(1, 1, 0), position=IK_EE_pos, rotation=(0, 0, 0))
    mc.parentConstraint(IK_EE_CTL, ikhandel)

    IK_04_pos = mc.xform(f'{prefix}_04_guide', q=True, ws=True, t=True)
    IK_04_CTL, IK_04_GRP = build_basic_control(name=f'{prefix}_IK_04', shape='circle', size=5.0, color_rgb=(1, 1, 0), position=IK_04_pos, rotation=(0, 0, 0))
    mc.parentConstraint(IK_04_CTL, f"{prefix}_04_IK_jnt")
    mc.parent(IK_04_GRP, IK_EE_CTL)
    for num in ['01', '02', '03', '04']:
        mc.parentConstraint(f'{prefix}_{num}_IK_jnt', f'{prefix}_{num}_bind_jnt', mo=True)
        mc.connectAttr(f'{FKIKSwitch_CTL}.FK_IK', f'{prefix}_{num}_bind_jnt_parentConstraint1.{prefix}_{num}_FK_JNTW0')
        mc.connectAttr(f'{rev_node}.outputX', f'{prefix}_{num}_bind_jnt_parentConstraint1.{prefix}_{num}_IK_jntW1')
    mc.pointConstraint( f'{prefix}_01_bind_jnt', FKIKSwitch_GRP, mo=True)
    mc.orienrConstraint(f'{prefix}_IK_EE_CTRL', f'{prefix}_03_IK_jnt')
    ##End


    mc.addAttr(f'{prefix}_FeatherShaper_CTRL', longName="Full_Bend", attributeType="bool", defaultValue=True, keyable=True)
    mc.addAttr(f'{prefix}_FeatherShaper_CTRL', longName="Full_Twist", attributeType="bool", defaultValue=True, keyable=True)
    mult_node2 = mc.createNode("multiplyDivide", name=f"{prefix}_Shape_multNode")
    mc.connectAttr(f'{prefix}_FeatherShaper_CTRL.Full_Bend', f"{mult_node2}.input2X")
    mc.connectAttr(f'{prefix}_FeatherShaper_CTRL.Full_Twist', f"{mult_node2}.input2Y")
    mc.connectAttr(f"{prefix}_FeatherShaper_CTRL.rotateX", f"{mult_node2}.input1X")
    mc.connectAttr(f"{prefix}_FeatherShaper_CTRL.rotateY", f"{mult_node2}.input1Y")
    for rotoff in rot_offset_list:
        parts = rotoff.split('_')
    
         # The identifier is the second-to-last element
        identifier = parts[-2]
    
        if identifier == "base":
            mc.connectAttr(f"{prefix}_FeatherShaper_CTRL.rotateX", f"{rotoff}.rotateX")
            mc.connectAttr(f"{prefix}_FeatherShaper_CTRL.rotateY", f"{rotoff}.rotateY")
        else:
            mc.connectAttr(f"{mult_node2}.outputX", f"{rotoff}.rotateX")
            mc.connectAttr(f"{mult_node2}.outputY", f"{rotoff}.rotateY")

    max_val = 20

    # Objects
    control = f"{prefix}_Span_CTRL"
    # 1. Add custom attributes
    if not mc.objExists(f"{control}.span_mult"):
        mc.addAttr(control, longName="span_mult", attributeType="double", defaultValue=1.0, keyable=True)
    if not mc.objExists(f"{control}.sensitivity"):
        mc.addAttr(control, longName="sensitivity", attributeType="double", defaultValue=1.0, keyable=True)

    # 2. Create MultiplyDivide node
    mult_node = mc.createNode("multiplyDivide", name=f"{control}_span_multNode")
    blend = mc.createNode("blendColors", name=f"{control}_span_blend")
    mc.connectAttr(f"{prefix}_Span_CTRL.translateX", f"{blend}.color1R")

    # 3. Create remapValue node
    remap_node = mc.createNode("remapValue", name=f"{control}_span_remapNode")
    mc.setAttr(f"{remap_node}.inputMin", -max_val)
    mc.setAttr(f"{remap_node}.inputMax", max_val)
    mc.setAttr(f"{remap_node}.outputMin", 0)
    mc.setAttr(f"{remap_node}.outputMax", 2.0)

    # 4. Connect translateX to multiplyDivide input1X
    mc.connectAttr(f"{blend}.outputR", f"{mult_node}.input1X")

    # 5. Connect sensitivity and span_mult to input2 channels
    mc.connectAttr(f"{control}.sensitivity", f"{mult_node}.input2X")
    mc.connectAttr(f"{control}.span_mult", f"{mult_node}.input2Y")

    # 6. Connect multiplyDivide output to remapValue input
    mc.connectAttr(f"{mult_node}.outputX", f"{remap_node}.inputValue")

    # 7. Connect remapValue output to multiplyDivide input1Y
    mc.connectAttr(f"{remap_node}.outValue", f"{mult_node}.input1Y")

    # 8. Connect multiplyDivide outputY to target joint scaleX
    for aimjnt in full_aimjnt_list:
        mc.connectAttr(f"{mult_node}.outputY", f"{aimjnt}.scaleX")
    #FOLD Logic
    mc.addAttr(f'{prefix}_Close_CTRL', longName="Jnt01_Mult", attributeType="double", defaultValue=0, keyable=True)
    mc.addAttr(f'{prefix}_Close_CTRL', longName="Jnt02_Mult", attributeType="double", defaultValue=1, keyable=True)
    mc.addAttr(f'{prefix}_Close_CTRL', longName="Jnt03_Mult", attributeType="double", defaultValue=1, keyable=True)
    mc.addAttr(f'{prefix}_Close_CTRL', longName="Jnt04_Mult", attributeType="double", defaultValue=1, keyable=True)
    mc.addAttr(f'{prefix}_Close_CTRL', longName="Span_Mult", attributeType="double", defaultValue=1, keyable=True)
    mc.addAttr(f'{prefix}_Close_CTRL', longName="Driver_Mult", attributeType="double", defaultValue=1, keyable=True)

    in_value = -5
    fold_01 = -40
    fold_02 = 100
    fold_03 = -140
    fold_span = -40
    
    remap_node_01 = mc.createNode("remapValue", name=f"{prefix}_01fold_remapNode")
    mc.setAttr(f"{remap_node_01}.inputMin", -in_value)
    mc.setAttr(f"{remap_node_01}.inputMax", in_value)
    mc.setAttr(f"{remap_node_01}.outputMin", -fold_01)
    mc.setAttr(f"{remap_node_01}.outputMax", fold_01)

    remap_node_02 = mc.createNode("remapValue", name=f"{prefix}_02fold_remapNode")
    mc.setAttr(f"{remap_node_02}.inputMin", -in_value)
    mc.setAttr(f"{remap_node_02}.inputMax", in_value)
    mc.setAttr(f"{remap_node_02}.outputMin", -fold_02)
    mc.setAttr(f"{remap_node_02}.outputMax", fold_02)

    remap_node_03 = mc.createNode("remapValue", name=f"{prefix}_03fold_remapNode")
    mc.setAttr(f"{remap_node_03}.inputMin", -in_value)
    mc.setAttr(f"{remap_node_03}.inputMax", in_value)
    mc.setAttr(f"{remap_node_03}.outputMin", -fold_03)
    mc.setAttr(f"{remap_node_03}.outputMax", fold_03)

    remap_node_span = mc.createNode("remapValue", name=f"{prefix}_spanfold_remapNode")
    mc.setAttr(f"{remap_node_span}.inputMin", 0)
    mc.setAttr(f"{remap_node_span}.inputMax", in_value)
    mc.setAttr(f"{remap_node_span}.outputMin", 1)
    mc.setAttr(f"{remap_node_span}.outputMax", fold_span)
    
    mult_node3 = mc.createNode("multiplyDivide", name=f"{prefix}_fold_multNode")
    mult_node4 = mc.createNode("multiplyDivide", name=f"{prefix}_folding_multNode")
    
    mc.connectAttr(f'{prefix}_Close_CTRL.Driver_Mult', f"{mult_node3}.input2X")
    mc.connectAttr(f'{prefix}_Close_CTRL.translateX', f"{mult_node3}.input1X")

    mc.connectAttr(f"{mult_node3}.outputX", f'{remap_node_01}.inputValue')
    mc.connectAttr(f'{remap_node_01}.outValue', f'{mult_node4}.input1X')
    mc.connectAttr(f'{prefix}_Close_CTRL.Jnt01_Mult', f"{mult_node4}.input2X")
    mc.connectAttr(f"{mult_node4}.outputX", f'{prefix}_01_FK_ArmClose_offset.rotateX')

    mc.connectAttr(f"{mult_node3}.outputX", f'{remap_node_02}.inputValue')
    mc.connectAttr(f'{remap_node_02}.outValue', f'{mult_node4}.input1Y')
    mc.connectAttr(f'{prefix}_Close_CTRL.Jnt02_Mult', f"{mult_node4}.input2Y")
    mc.connectAttr(f"{mult_node4}.outputY", f'{prefix}_02_FK_ArmClose_offset.rotateX')
    
    mc.connectAttr(f"{mult_node3}.outputX", f'{remap_node_03}.inputValue')
    mc.connectAttr(f'{remap_node_03}.outValue', f'{mult_node4}.input1Z')
    mc.connectAttr(f'{prefix}_Close_CTRL.Jnt03_Mult', f"{mult_node4}.input2Z")
    mc.connectAttr(f"{mult_node4}.outputZ", f'{prefix}_03_FK_ArmClose_offset.rotateX')
    mc.connectAttr(f"{mult_node3}.outputX", f'{remap_node_span}.inputValue')
    mc.connectAttr(f'{remap_node_span}.outValue', f"{blend}.color2R")

    aimremap_node_01 = mc.createNode("remapValue", name=f"{prefix}_01foldaim_remapNode")
    mc.setAttr(f"{aimremap_node_01}.inputMin", -in_value)
    mc.setAttr(f"{aimremap_node_01}.inputMax", in_value)
    mc.setAttr(f"{aimremap_node_01}.outputMin", -7)
    mc.setAttr(f"{aimremap_node_01}.outputMax", 7)

    aimremap_node_02 = mc.createNode("remapValue", name=f"{prefix}_02foldaim_remapNode")
    mc.setAttr(f"{aimremap_node_02}.inputMin", -in_value)
    mc.setAttr(f"{aimremap_node_02}.inputMax", in_value)
    mc.setAttr(f"{aimremap_node_02}.outputMin", 20)
    mc.setAttr(f"{aimremap_node_02}.outputMax", -20)

    aimremap_node_03 = mc.createNode("remapValue", name=f"{prefix}_03foldaim_remapNode")
    mc.setAttr(f"{aimremap_node_03}.inputMin", -in_value)
    mc.setAttr(f"{aimremap_node_03}.inputMax", in_value)
    mc.setAttr(f"{aimremap_node_03}.outputMin", -13)
    mc.setAttr(f"{aimremap_node_03}.outputMax", 13)

    aimremap_node_04 = mc.createNode("remapValue", name=f"{prefix}_04foldaim_remapNode")
    mc.setAttr(f"{aimremap_node_04}.inputMin", -in_value)
    mc.setAttr(f"{aimremap_node_04}.inputMax", in_value)
    mc.setAttr(f"{aimremap_node_04}.outputMin", -7)
    mc.setAttr(f"{aimremap_node_04}.outputMax", 7)

    aimremap_node_05 = mc.createNode("remapValue", name=f"{prefix}_05foldaim_remapNode")
    mc.setAttr(f"{aimremap_node_05}.inputMin", -in_value)
    mc.setAttr(f"{aimremap_node_05}.inputMax", in_value)
    mc.setAttr(f"{aimremap_node_05}.outputMin", -5)
    mc.setAttr(f"{aimremap_node_05}.outputMax", 5)

    mc.connectAttr(f"{mult_node3}.outputX", f'{aimremap_node_01}.inputValue')
    mc.connectAttr(f'{aimremap_node_01}.outValue', f'{prefix}Aim_01_ArmClose_offset.translateX')
    mc.connectAttr(f"{mult_node3}.outputX", f'{aimremap_node_02}.inputValue')
    mc.connectAttr(f'{aimremap_node_02}.outValue', f'{prefix}Aim_02_ArmClose_offset.translateX')
    mc.connectAttr(f"{mult_node3}.outputX", f'{aimremap_node_03}.inputValue')
    mc.connectAttr(f'{aimremap_node_03}.outValue', f'{prefix}Aim_02_ArmClose_offset.translateY')
    mc.connectAttr(f"{mult_node3}.outputX", f'{aimremap_node_04}.inputValue')
    mc.connectAttr(f'{aimremap_node_04}.outValue', f'{prefix}Aim_03_ArmClose_offset.translateX')
    mc.connectAttr(f"{mult_node3}.outputX", f'{aimremap_node_05}.inputValue')
    mc.connectAttr(f'{aimremap_node_05}.outValue', f'{prefix}Aim_03_ArmClose_offset.translateY')

    #Clean Up Wing

    mc.group(f'{prefix}_01_FK_JNT', f'{prefix}_01_IK_jnt', f'{prefix}_ikHandle', f'{prefix}_Main_loft', name=f'{prefix}_extraOffset_GRP')
    mc.parent(f'{prefix}_Close_GRP', f'{prefix}_01_FK_CTRL')
    mc.delete(f'{prefix}_curve', f'{prefix}_curve1')
    mc.parent(f'{prefix}_IK_Aim_GRP', f'{prefix}_IK_Root_CTRL' )
    mc.parent(f'{prefix}_IK_EE_GRP', f'{prefix}_IK_Root_CTRL' )
    mc.parent(f'{prefix}_Span_GRP', world=True)
    mc.parentConstraint(f'{prefix}_IK_EE_CTRL', f'{prefix}_Span_GRP', mo=True)
    mc.parentConstraint(f'{prefix}_03_FK_CTRL', f'{prefix}_Span_GRP', mo=True)
    mc.group(f'{prefix}_Main_Feather_aim_01_GRP', f'{prefix}_Main_Feather_aim_02_GRP', f'{prefix}_Main_Feather_aim_03_GRP', f'{prefix}_Main_Feather_aim_04_GRP', name = f'{prefix}_aimcurve_GRP')
    mc.parent(f'{prefix}_01_FK_GRP', fk_group)
    mc.parent(f'{prefix}_IK_Root_GRP', ik_group)
    mc.connectAttr(f'{FKIKSwitch_CTL}.FK_IK', f'{prefix}_FK_grp.visibility')
    mc.connectAttr(f'{rev_node}.outputX', f'{prefix}_IK_grp.visibility')
    mc.connectAttr(f'{FKIKSwitch_CTL}.FK_IK', f'{prefix}_Span_GRP_parentConstraint1.Wing_L_03_FK_CTRLW1')
    mc.connectAttr(f'{rev_node}.outputX', f'{prefix}_Span_GRP_parentConstraint1.{prefix}_IK_EE_CTRLW0')

    




build_wing(group='Wing_L_guides')   
    
    
    