import maya.cmds as mc

try:
    from PySide6 import QtWidgets, QtCore
    from PySide6.QtWidgets import QDialog
except ImportError:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtWidgets import QDialog

import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

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

    #build_basic_control(name='name', size=10, color_rgb=(1,1,0), position=(0,0,0), rotation=(0,0,0))

def create_display_layer(layer_name, objects, color_index, is_reference=False):
    if not mc.objExists(layer_name):
        mc.createDisplayLayer(name=layer_name, number=1, nr=True)
    
    # Adding objects to the layer
    mc.editDisplayLayerMembers(layer_name, objects)
    
    # Set the display type for reference layers
    if is_reference:
        mc.setAttr(f"{layer_name}.displayType", 2)  # Reference display type

    # Remove color for the RIG layer (if the layer is RIG_Display)
        # Set the color for all other layers (unless it's RIG_Display)
        mc.setAttr(f"{layer_name}.color", color_index)

    # Set general visibility and layer settings
    mc.setAttr(f"{layer_name}.visibility", 1)


def get_model_center(model_grp):
    all_geo = mc.listRelatives(model_grp, allDescendents=True, type='transform', fullPath=True) or []
    geo_shapes = []

    for obj in all_geo:
        shapes = mc.listRelatives(obj, shapes=True, fullPath=True) or []
        if any(mc.nodeType(s) in ['mesh', 'nurbsSurface', 'nurbsCurve'] for s in shapes):
            geo_shapes.append(obj)

    if not geo_shapes:
        mc.error(f"No geometry found under {model_grp}.")

    # Get bounding box of all geo
    min_x, min_y, min_z = [float('inf')] * 3
    max_x, max_y, max_z = [float('-inf')] * 3

    for geo in geo_shapes:
        bbox = mc.exactWorldBoundingBox(geo)
        min_x = min(min_x, bbox[0])
        min_y = min(min_y, bbox[1])
        min_z = min(min_z, bbox[2])
        max_x = max(max_x, bbox[3])
        max_y = max(max_y, bbox[4])
        max_z = max(max_z, bbox[5])

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center_z = (min_z + max_z) / 2.0

    return [center_x, center_y, center_z]

def build_roll_rig(rig_prefix, rig_size):
    
    build_basic_control(
        name=f'{rig_prefix}_Roll',
        size=1 * rig_size,
        color_rgb=(1, .05, .05),
        position=(0, 0, 0),  # Positioned at the origin
        rotation=(0, 0, 0)   # No rotation
        )
    
    build_basic_control(
        name=f'{rig_prefix}_RollPath',  # Name with rig_prefix
        size=3 * rig_size,  # 3 times the rig_size argument
        color_rgb=(0.90, 0.38, 0.34),  # #e66057 in RGB
        position=(0, 0, 0),  # Positioned at the origin
        rotation=(0, 0, 0)   # No rotation
    )

    roll = f'{rig_prefix}_Roll_CTRL'
    roll_path =f'{rig_prefix}_RollPath_CTRL'
    main = f'{rig_prefix}_Main_CTRL'
    main_jnt = f'{rig_prefix}_main_jnt'
    roll_shape = f'{rig_prefix}_RollPath_CTRLShape'

    loc = mc.spaceLocator(name='pivot_loc')[0]

    # Create the Nearest Point on Curve node
    npc_node = mc.createNode('nearestPointOnCurve', name='roll_nearestPointOnCurve')

    # Connect the world space output of the curve shape to the inputCurve
    mc.connectAttr(f'{roll_shape}.worldSpace[0]', f'{npc_node}.inputCurve', force=True)

    # Connect the transform of roll[0] into the inPosition of the nearestPointOnCurve
    mc.connectAttr(f'{roll}.translate', f'{npc_node}.inPosition', force=True)

    mc.connectAttr(f'{npc_node}.position', f'{loc}.translate', force=True)

    # Connect loc.translate to main.rotatePivot
    mc.connectAttr(f'{loc}.translate', f'{main}.rotatePivot', force=True)

    # Connect loc.translate to main_jnt.rotatePivot
    mc.connectAttr(f'{loc}.translate', f'{main_jnt}.rotatePivot', force=True)

    md1 = mc.createNode('multiplyDivide', name='roll_translateY_mult1')
    md2 = mc.createNode('multiplyDivide', name='roll_translateY_mult2')

    # Get the Y translate from roll[0]
    # Connect roll[0].translateY → md1.input1X, input1Y, input1Z
    mc.connectAttr(f'{roll}.translateY', f'{md1}.input1X', force=True)
    mc.connectAttr(f'{roll}.translateY', f'{md1}.input1Y', force=True)
    mc.connectAttr(f'{roll}.translateY', f'{md1}.input1Z', force=True)

    # Set md1.input2 values to (-0.2, 0.2, 0.2)
    mc.setAttr(f'{md1}.input2X', -0.2)
    mc.setAttr(f'{md1}.input2Y',  0.2)
    mc.setAttr(f'{md1}.input2Z',  0.2)

    # Connect md1.output → md2.input2
    mc.connectAttr(f'{md1}.output', f'{md2}.input2', force=True)

    # Connect roll[0].translate → md2.input1
    mc.connectAttr(f'{roll}.translate', f'{md2}.input1', force=True)

    # Connect md2.outputX → main.rotateZ
    mc.connectAttr(f'{md2}.outputX', f'{main}.rotateZ', force=True)

    # Connect md2.outputX → main.rotateX
    mc.connectAttr(f'{md2}.outputZ', f'{main}.rotateX', force=True)

    mc.hide(loc)
    mc.parent(f'{rig_prefix}_Roll_GRP', f'{rig_prefix}_Offset_CTRL')
    mc.parent(f'{rig_prefix}_RollPath_GRP', f'{rig_prefix}_Offset_CTRL')
    mc.parent(loc, f'{rig_prefix}_Offset_CTRL')


def mirror_guide(guide):
    """
    Mirrors a single guide across the X axis.
    Must be named with prefix 'L_'. The mirrored guide will be named with 'R_'.
    If the R_ version already exists, it will be deleted.

    Args:
        guide (str): Name of the original guide to mirror.
    """
    if not mc.objExists(guide):
        print(f"Guide '{guide}' does not exist. Skipping.")
        return None

    if not guide.startswith("L_"):
        print(f"Skipping {guide} — not prefixed with 'L_'.")
        return None

    mirrored_name = guide.replace("L_", "R_", 1)

    # Delete existing R_ guide if it exists
    if mc.objExists(mirrored_name):
        mc.delete(mirrored_name)
        print(f"Deleted existing guide: {mirrored_name}")

    # Duplicate the guide and rename
    mc.select(guide) 
    duplicated = mc.duplicate(guide, name=mirrored_name)
    if not duplicated:
        print(f"Failed to duplicate guide: {guide}")
        return None

    mirrored = duplicated[0]

    # Mirror position manually (flip X)
    pos = mc.xform(guide, q=True, ws=True, t=True)
    mirrored_pos = [-pos[0], pos[1], pos[2]]
    mc.xform(mirrored, ws=True, t=mirrored_pos)

    # Mirror rotation (flip Y and Z)
    rot = mc.xform(guide, q=True, ws=True, rotation=True)
    mirrored_rot = [rot[0], -rot[1], -rot[2]]
    mc.xform(mirrored, ws=True, rotation=mirrored_rot)

    print(f"Mirrored: {guide} → {mirrored}")
    return mirrored

def control_from_guide(guide, ctrl_name=None, size=1.0, color_rgb=(1, 1, 0)):
    """
    Creates a control that matches the position and rotation of the guide.

    Args:
        guide (str): Name of the guide object.
        ctrl_name (str): Optional name for the control.
        size (float): Control size.
        color_rgb (tuple): RGB color of control.
    
    Returns:
        Tuple[str, str]: (Control name, Offset group name)
    """
    if not mc.objExists(guide):
        mc.error(f"Guide '{guide}' does not exist.")
        return None, None

    if not ctrl_name:
        ctrl_name = guide.replace("_guide", "")

    pos = mc.xform(guide, q=True, ws=True, t=True)
    rot = mc.xform(guide, q=True, ws=True, ro=True)

    ctrl, offset = build_basic_control(
        name=ctrl_name,
        size=size,
        color_rgb=color_rgb,
        position=pos,
        rotation=rot
    )

    print(f"Created control: {ctrl} matching guide: {guide}")
    return ctrl, offset

def simple_joint(guide, joint_name=None):
    """
    Creates a joint at the guide's location with matching orientation.

    Args:
        guide (str): The guide to use as reference.
        joint_name (str): Optional custom joint name. Defaults to guide.replace("_guide", "_jnt")
    
    Returns:
        str: The name of the created joint.
    """
    if not mc.objExists(guide):
        mc.error(f"Guide '{guide}' does not exist.")
        return None

    if not joint_name:
        joint_name = guide.replace("_guide", "_jnt")

    # Get world position and orientation
    pos = mc.xform(guide, q=True, ws=True, t=True)
    rot = mc.xform(guide, q=True, ws=True, ro=True)

    # Create the joint
    joint = mc.joint(name=joint_name, position=pos)
    mc.xform(joint, ws=True, rotation=rot)

    print(f"Created joint: {joint} at {pos} with rotation {rot}")
    return joint



def build():
    """
    Main function that looks for a group named 'Guides' and mirrors any guide
    inside it that starts with 'L_' using mirror_guide().
    """
    if not mc.objExists("Guides"):
        mc.error("No 'Guides' group found in the scene.")

    # Get children of the Guides group
    guide_list = mc.listRelatives("Guides", children=True, type="transform", fullPath=False) or []

    for guide in guide_list:
        if guide.startswith("L_"):
            mirror_guide(guide)
        else:
            print(f"Skipping {guide} — not an L_ guide.")


# Example usage:
build()