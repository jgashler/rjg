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
    #add_to_face_bind_set(jnt)
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






def build_ribbon(
    guide_list=[],
    fromrig=False,
    Control_List=[],
    axis='x',
    ribbon_width=0.5,
    prefix=None,
    parent_type='single',
    parent=None,
    parent_list=[],
    parent_joint=None
):
    """
    Build a ribbon rig using guides, with option for rig-driven or control-driven setup.

    Args:
        guide_list (list): List of guide transforms in order.
        fromrig (bool): If True, use existing rig joints under "SKEL". If False, build new controls/joints.
        Control_List (list): Control names to create if fromrig=False.
        axis (str): Axis to offset curves ('x', 'y', or 'z').
        ribbon_width (float): Distance from center curve to each side curve.
        prefix (str): Prefix for naming.
        parent_type (str): 'single' or 'list' parenting style.
        parent (str): Parent transform for single parent mode.
        parent_list (list): Parent transforms for list parenting mode.
        parent_joint (str): Parent joint for ribbon joints.

    Returns:
        dict: Created ribbon nodes for further use.
    """
    if not guide_list or len(guide_list) < 2:
        mc.warning("Not enough guides to build a ribbon.")
        return {}

    if not prefix:
        prefix = "Ribbon"

    # ---------------------------------------------
    # STEP 1: Build main curve from guides
    # ---------------------------------------------
    main_curve = build_curve(guide_list, prefix=prefix)
    if not main_curve:
        return {}

    # ---------------------------------------------
    # STEP 2: Offset curves along chosen axis
    # ---------------------------------------------
    offset_axis = {'x': (1,0,0), 'y': (0,1,0), 'z': (0,0,1)}.get(axis.lower())
    if not offset_axis:
        raise ValueError(f"Invalid axis '{axis}', must be x, y, or z.")

    # Positive curve
    pos_curve = mc.duplicate(main_curve, name=f"{prefix}_pos_crv")[0]
    mc.move(ribbon_width*offset_axis[0], ribbon_width*offset_axis[1], ribbon_width*offset_axis[2], pos_curve, r=True)

    # Negative curve
    neg_curve = mc.duplicate(main_curve, name=f"{prefix}_neg_crv")[0]
    mc.move(-ribbon_width*offset_axis[0], -ribbon_width*offset_axis[1], -ribbon_width*offset_axis[2], neg_curve, r=True)

    # ---------------------------------------------
    # STEP 3: Loft surface between the two curves
    # ---------------------------------------------
    ribbon_surface = mc.loft(pos_curve, neg_curve, ch=True, u=True, c=False, ar=True, d=1, ss=1, n=f"{prefix}_ribbon")[0]

    # ---------------------------------------------
    # STEP 4: Create joints for each guide + UV pin
    # ---------------------------------------------
    ribbon_joints = []
    ribbon_offset = mc.group(em=True, name=f"{prefix}_ribbon_offset")
    for guide in guide_list:
        guide_name = guide.split('|')[-1]
        pos = mc.xform(guide_name, q=True, ws=True, t=True)
        jnt = mc.joint(name=f"{prefix}_{guide_name}_bindjnt", p=pos)
        ribbon_joints.append(jnt)
        transfrom = mc.group(em=True, name=f"{prefix}_{guide_name}_pin")
        mc.xform(transfrom, ws=True, t=pos)
        mc.parent(transfrom, ribbon_offset)

        # UVPin setup
        mc.select(clear=True)
        mc.select(ribbon_surface, transfrom)
        mc.UVPin()
        mc.select(clear=True)
        mc.parentConstraint(transfrom, jnt, mo=True)
        # Parent under parent_joint if specified
        if parent_joint and mc.objExists(parent_joint):
            mc.parent(jnt, parent_joint)

    # ---------------------------------------------
    # STEP 5: Binding setup
    # ---------------------------------------------
    if fromrig:
        # Bind all SKEL joints
        bind_joints = mc.listRelatives("SKEL", ad=True, type="joint") or []
        mc.skinCluster(bind_joints, ribbon_surface, tsb=True, nw=2, bm=0, sm=0, dr=4, n=f'{prefix}_cluster')
    else:
        # Build controls + bind ribbon_joints
        controls = []
        offsets = []
        control_jnts = []
        for guide in Control_List:
            jnt,ctrl,offset = Simple_joint_and_Control(
                guide,
                prefix=f"{prefix}",
                CTRL_Color=(0, 0, 1),
                CTRL_Size=0.2,
                JNT_Size=0.5
            )
            #print(ctrl,offset,jnt)
            mc.parent(jnt,ribbon_offset)
            controls.append(ctrl)
            offsets.append(offset)
            control_jnts.append(jnt)

        mc.select(*control_jnts, ribbon_surface)
        #print(*control_jnts, ribbon_surface)
        mc.skinCluster( tsb=True, nw=2, bm=0, sm=0, dr=4, name=f'{prefix}_cluster')

    # ---------------------------------------------
    # STEP 6: Parenting
    # ---------------------------------------------
    if fromrig == False:
        if parent_type == 'single' and parent:
            # Parent all offsets to single parent
            for ctrl in offsets:
                if mc.objExists(ctrl):
                    mc.parent(ctrl, parent)

        elif parent_type == 'list' and parent and parent_list:
            # Parent offsets under single parent, then constrain each
            for i, ctrl in enumerate(offsets):
                if mc.objExists(ctrl):
                    mc.parent(ctrl, parent)
                    if i < len(parent_list):
                        mc.parentConstraint(parent_list[i], ctrl, mo=True)


    mc.delete(neg_curve, pos_curve, main_curve)
    mc.parent(ribbon_surface, ribbon_offset)
    if mc.objExists('ROOT'):
        mc.parent(ribbon_offset, 'RIG')
