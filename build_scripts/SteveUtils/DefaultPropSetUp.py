import maya.cmds as mc
import re

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

def build_simplecluster_rig(rig_prefix='cluster', rig_size=1.0, auto_skin=False, clear_guide=False):
    import re
    import maya.cmds as mc

    # Find all guides matching pattern
    all_guides = mc.ls(f'cluster_guide_*', type='transform') or []

    def extract_index(name):
        match = re.search(rf'cluster_guide_(\d+)', name)
        return int(match.group(1)) if match else -1

    sorted_guides = sorted(all_guides, key=extract_index)

    if not sorted_guides:
        mc.error(f"No guides found matching pattern: cluster_guide_XX")

    created_joints = []
    created_ctrl_grps = []

    for i, guide in enumerate(sorted_guides, 1):
        pos = mc.xform(guide, q=True, t=True, ws=True)
        rot = mc.xform(guide, q=True, ro=True, ws=True)

        ctrl_name = f'{rig_prefix}_{str(i).zfill(2)}'
        jnt_name = f'{ctrl_name}_jnt'

        # Create control
        build_basic_control(
            name=ctrl_name,
            size=2 * rig_size,
            color_rgb=(0.3, 0.7, 1),
            position=pos,
            rotation=rot
        )

        # Save control group name
        ctrl_grp_name = f'{ctrl_name}_GRP'
        created_ctrl_grps.append(ctrl_grp_name)

        # Create joint
        mc.select(clear=True)
        jnt = mc.joint(p=pos, name=jnt_name)
        mc.joint(jnt, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        mc.makeIdentity(jnt, apply=True, t=1, r=1, s=1, n=0)
        created_joints.append(jnt)

        # Parent constraints from control to joint
        mc.parentConstraint(f"{ctrl_name}_CTRL", jnt, mo=False)
        mc.scaleConstraint(f"{ctrl_name}_CTRL", jnt, mo=False)

    # Group all controls
    cluster_ctrl_grp = f'{rig_prefix}_Cluster_ctrl_grp'
    if mc.objExists(cluster_ctrl_grp):
        mc.delete(cluster_ctrl_grp)
    mc.group(created_ctrl_grps, name=cluster_ctrl_grp)

    # Parent cluster controls group under main control
    mc.parent(cluster_ctrl_grp, f'{rig_prefix}_Main_CTRL')

    # Parent all joints under main joint
    for jnt in created_joints:
        if jnt != f'{rig_prefix}_main_jnt':
            mc.parent(jnt, f'{rig_prefix}_main_jnt')

    if auto_skin:
        main_jnt = created_joints
        model_grp = 'MODEL'

        geo_list = mc.listRelatives(model_grp, allDescendents=True, type='mesh', fullPath=False) or []
        geo_transforms = list({mc.listRelatives(mesh, parent=True, fullPath=True)[0] for mesh in geo_list})

        for geo in geo_transforms:
            try:
                mc.select([geo] + main_jnt)
                mc.skinCluster(toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1, weightDistribution=0)
            except Exception as e:
                print(f"Failed to skin {geo}: {e}")

    # Parent first joint under main joint if it exists
    if mc.objExists(f'{rig_prefix}_main_jnt') and created_joints:
        mc.parent(created_joints[0], f'{rig_prefix}_main_jnt')

    # Parent the first control group to main control (optional, but you can remove if redundant)
    if created_ctrl_grps:
        mc.parent(created_ctrl_grps[0], f'{rig_prefix}_Main_CTRL')

    if clear_guide:
        mc.delete(sorted_guides)

    return created_joints

def build_guides(pivot):
    valid_pivots = ['cluster', 'chain', 'simplechain', 'guide']
    
    if pivot not in valid_pivots:
        print("No guides needed")
        return
    
    # Clear existing guides of relevant names if you want (optional)
    # For example:
    # if mc.objExists('MainControl_guide'): mc.delete('MainControl_guide')
    # if mc.objExists('chain_guide_01'): mc.delete('chain_guide_01')
    # if mc.objExists('cluster_guide_01'): mc.delete('cluster_guide_01')
    
    if pivot == 'guide':
        if not mc.objExists('MainControl_guide'):
            mc.spaceLocator(name='MainControl_guide')
            mc.xform('MainControl_guide', ws=True, t=[0,0,0])
        else:
            print('Locator "MainControl_guide" already exists.')
    
    elif pivot in ['chain', 'simplechain']:
        if not mc.objExists('chain_guide_01'):
            mc.spaceLocator(name='chain_guide_01')
            mc.xform('chain_guide_01', ws=True, t=[0,0,0])
        else:
            print('Locator "chain_guide_01" already exists.')
    
    elif pivot == 'cluster':
        if not mc.objExists('cluster_guide_01'):
            mc.spaceLocator(name='cluster_guide_01')
            mc.xform('cluster_guide_01', ws=True, t=[0,0,0])
        else:
            print('Locator "cluster_guide_01" already exists.')

def build_simplechain_rig(rig_prefix='chain', rig_size=1.0, auto_skin=False, clear_guide=False):
    """
    Builds a chain-style FK rig based on guide locators named chain_guide_01, chain_guide_02, etc.
    """
    # Find all guides matching pattern
    all_guides = mc.ls(f'chain_guide_*', type='transform') or []

    # Filter and sort by index
    def extract_index(name):
        match = re.search(rf'chain_guide_(\d+)', name)
        return int(match.group(1)) if match else -1

    sorted_guides = sorted(all_guides, key=extract_index)

    if not sorted_guides:
        mc.error(f"No guides found matching pattern: chain_guide_XX")

    created_joints = []
    previous_ctrl = None
    previous_joint = None

    for i, guide in enumerate(sorted_guides, 1):
        # Get guide transform
        pos = mc.xform(guide, q=True, t=True, ws=True)
        rot = mc.xform(guide, q=True, ro=True, ws=True)

        ctrl_name = f'{rig_prefix}_{str(i).zfill(2)}'
        jnt_name = f'{ctrl_name}_jnt'

        # Create control
        build_basic_control(
            name=ctrl_name,
            size=2 * rig_size,
            color_rgb=(0.3, 0.7, 1),  # Cyan color for chain
            position=pos,
            rotation=rot
        )

        # Create joint
        mc.select(clear=True)
        jnt = mc.joint(p=pos, name=jnt_name)
        mc.joint(jnt, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        mc.makeIdentity(jnt, apply=True, t=1, r=1, s=1, n=0)
        created_joints.append(jnt)

        # Parent constraints
        mc.parentConstraint(f"{ctrl_name}_CTRL", jnt, mo=False)
        mc.scaleConstraint(f"{ctrl_name}_CTRL", jnt, mo=False)

        # Parent FK hierarchy
        if previous_ctrl:
            mc.parent(f"{ctrl_name}_GRP", f"{previous_ctrl}_CTRL")
            mc.parent(f"{ctrl_name}_jnt", f"{previous_ctrl}_jnt")

        previous_ctrl = ctrl_name

        #if previous_ctrl:


    if auto_skin:
            main_jnt = created_joints
            model_grp = 'MODEL'
            
            # Get all geometry under MODEL, including nested children
            geo_list = mc.listRelatives(model_grp, allDescendents=True, type='mesh', fullPath=False) or []

            # Convert mesh shape nodes to transform nodes (geometry group)
            geo_transforms = list({mc.listRelatives(mesh, parent=True, fullPath=True)[0] for mesh in geo_list})

            # Bind each geo to the main joint
            for geo in geo_transforms:
                try:
                    mc.select([geo] + main_jnt)
                    mc.skinCluster(toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1, weightDistribution=0)
                except Exception as e:
                    print(f"Failed to skin {geo}: {e}")

    mc.parent(f'{rig_prefix}_01_GRP', f'{rig_prefix}_Main_CTRL')
    mc.parent(f'{rig_prefix}_01_jnt', f'{rig_prefix}_main_jnt')
    if clear_guide == True:
        mc.delete(sorted_guides)
    return created_joints

def connect_ik_spline_channels_to_main_ctrl(rig_prefix, ik_handle, main_ctrl):
    import maya.cmds as mc

    # List of attributes to connect
    attrs = [
        ('offset', 0.0),  # default value 0
        ('roll', 0.0),
        ('twist', 0.0)
    ]

    for attr, default in attrs:
        ctrl_attr = f'{main_ctrl}.{attr}'

        # Add attribute if it doesn't exist
        if not mc.attributeQuery(attr, node=main_ctrl, exists=True):
            mc.addAttr(main_ctrl, longName=attr, attributeType='float', keyable=True, defaultValue=default)
            mc.setAttr(ctrl_attr, default)

        # Check if the IK handle has the attribute before connecting
        if mc.attributeQuery(attr, node=ik_handle, exists=True):
            mc.connectAttr(ctrl_attr, f'{ik_handle}.{attr}', force=True)
        else:
            print(f"Warning: {ik_handle} has no attribute '{attr}'")

def add_ik_spline_cv_controls(ik_curve_name, rig_prefix='chain', rig_size=0.5):
    cvs = mc.getAttr(f"{ik_curve_name}.controlPoints[*]")
    cvs_count = len(cvs)

    cv_controls_grp = f'{rig_prefix}_IKSpline_CV_CTRLS_GRP'
    if mc.objExists(cv_controls_grp):
        mc.delete(cv_controls_grp)
    cv_controls_grp = mc.group(em=True, name=cv_controls_grp)

    cv_ctrl_names = []

    for i in range(cvs_count):
        # Create cluster for the CV
        cluster_handle = mc.cluster(f'{ik_curve_name}.cv[{i}]', name=f'{rig_prefix}_ikSpline_cv{i+1}_cluster')[1]

        # Get cluster position
        pos = mc.pointPosition(f'{ik_curve_name}.cv[{i}]', world=True)

        # Create control at cluster position
        ctrl_name = f'{rig_prefix}_ikSpline_cv{i+1}_CTRL'
        build_basic_control(
            name=ctrl_name,
            size=rig_size,
            color_rgb=(0.5, 1.0, 0.5),
            position=pos,
            rotation=[0, 0, 0]
        )

        # Parent cluster handle under control so moving control moves CV
        mc.parent(cluster_handle, f'{ctrl_name}_CTRL')

        # Parent control under CV controls group
        mc.parent(f'{ctrl_name}_GRP', cv_controls_grp)

        cv_ctrl_names.append(ctrl_name)

    return cv_ctrl_names, cv_controls_grp

def make_ik_spline_stretchy(rig_prefix, ik_curve_name, ik_joints, root_ctrl):

    # 1. Store original curve length on root_ctrl if not already there
    if not mc.attributeQuery('ikSplineOrigLength', node=root_ctrl, exists=True):
        orig_length = mc.arclen(ik_curve_name)
        mc.addAttr(root_ctrl, longName='ikSplineOrigLength', attributeType='double', keyable=False)
        mc.setAttr(f"{root_ctrl}.ikSplineOrigLength", orig_length)

    # 2. Create curveInfo node and connect curve worldSpace to it
    curve_info_node = f'{rig_prefix}_ikSpline_curveInfo'
    if not mc.objExists(curve_info_node):
        curve_info_node = mc.createNode('curveInfo', name=curve_info_node)
    mc.connectAttr(f'{ik_curve_name}.worldSpace[0]', f'{curve_info_node}.inputCurve', force=True)

    # 3. Create multiplyDivide node to calculate scale factor (current length / original length)
    mult_node = f'{rig_prefix}_ikSpline_scaleFactor'
    if not mc.objExists(mult_node):
        mult_node = mc.createNode('multiplyDivide', name=mult_node)
        mc.setAttr(f'{mult_node}.operation', 2)  # Divide
    mc.connectAttr(f'{curve_info_node}.arcLength', f'{mult_node}.input1X', force=True)
    mc.connectAttr(f'{root_ctrl}.ikSplineOrigLength', f'{mult_node}.input2X', force=True)

    # 4. Connect scale factor output to scaleX of each IK joint
    for jnt in ik_joints:
        mc.connectAttr(f'{mult_node}.outputX', f'{jnt}.scaleX', force=True)

def add_ik_spline_twist_controls(root_ctrl_name):
    """
    Adds startTwist and endTwist attributes to the root control and connects them to the IK handle.
    """
    if not mc.attributeQuery('startTwist', node=root_ctrl_name, exists=True):
        mc.addAttr(root_ctrl_name, longName='startTwist', attributeType='double', keyable=True)
    if not mc.attributeQuery('endTwist', node=root_ctrl_name, exists=True):
        mc.addAttr(root_ctrl_name, longName='endTwist', attributeType='double', keyable=True)

    ik_handle_name = f'{root_ctrl_name.split("_Root_CTRL")[0]}_ikSplineHandle'

    # Connect attributes to IK handle twist
    if mc.objExists(ik_handle_name):
        mc.connectAttr(f'{root_ctrl_name}.startTwist', f'{ik_handle_name}.twistStart', force=True)
        mc.connectAttr(f'{root_ctrl_name}.endTwist', f'{ik_handle_name}.twistEnd', force=True)

def connect_visibility_to_fkik_switch(root_ctrl, fkik_attr, ik_objects, fk_objects=None):

    # Create reverse node for FK visibility if needed
    if fk_objects:
        rev_node = mc.createNode('reverse', name=f'{root_ctrl}_fkIkSwitch_reverse')
        mc.connectAttr(f'{root_ctrl}.{fkik_attr}', f'{rev_node}.inputX', force=True)
        # Connect FK objects visibility to reverse output
        mc.connectAttr(f'{rev_node}.outputX', f'{fk_objects}.visibility', force=True)

    # Connect IK objects visibility directly to switch
    mc.connectAttr(f'{root_ctrl}.{fkik_attr}', f'{ik_objects}.visibility', force=True)


def create_ik_spline_handle_and_control(ik_joints, rig_prefix='chain', rig_size=1.0):
    """
    Builds an IK Spline handle from the IK joint chain and attaches it to a control.
    Returns the name of the IK control and the IK spline curve.
    """

    if len(ik_joints) < 2:
        mc.error("Not enough IK joints to create an IK spline handle.")

    # Delete existing IK handle if present
    ik_handle_name = f'{rig_prefix}_ikSplineHandle'
    ik_curve_name = f'{rig_prefix}_ikSplineCurve'
    if mc.objExists(ik_handle_name):
        mc.delete(ik_handle_name)
    if mc.objExists(ik_curve_name):
        mc.delete(ik_curve_name)

    # Create IK spline handle
    ik_handle, effector, ik_curve = mc.ikHandle(
        name=ik_handle_name,
        sj=ik_joints[0],
        ee=ik_joints[-1],
        sol='ikSplineSolver',
        createCurve=True
    )

    # Rename the IK curve to a consistent name
    ik_curve = mc.rename(ik_curve, ik_curve_name)

    # Create IK control at the end joint position
    end_pos = mc.xform(ik_joints[-1], q=True, t=True, ws=True)
    ik_ctrl_name = f'{rig_prefix}_IK'
    build_basic_control(
        name=ik_ctrl_name,
        size=3 * rig_size,
        color_rgb=(1, 1, 0),  # Yellow
        position=end_pos,
        rotation=[0, 0, 0]
    )

    # Parent the IK handle under the IK control
    mc.parent(ik_handle, f"{ik_ctrl_name}_CTRL")

    # Parent the IK curve under the rig root group
    if mc.objExists('RIG'):
        mc.parent(ik_curve, 'RIG')

    return ik_ctrl_name, ik_curve_name

def add_fkik_switch_and_blend(fk_joints, ik_joints, bind_joints, rig_prefix='chain'):
    root_ctrl = f"{rig_prefix}_Root_CTRL"

    # Add FK/IK switch attribute if it doesn't exist
    if not mc.attributeQuery('fkIkSwitch', node=root_ctrl, exists=True):
        mc.addAttr(root_ctrl, longName='fkIkSwitch', attributeType='float', min=0, max=1, defaultValue=0, keyable=True)

    for fk_jnt, ik_jnt, bind_jnt in zip(fk_joints, ik_joints, bind_joints):
        # Create parent constraint on bind joint with fk and ik as targets
        constraint_name = mc.parentConstraint(fk_jnt, ik_jnt, bind_jnt, mo=True)[0]

        # The parentConstraint weight attributes will be named like:
        # constraintName.target[0].targetWeight or constraintName.target[1].targetWeight
        # Usually target[0] is fk_jnt and target[1] is ik_jnt, but confirm order below

        # Get the weight attributes for each target
        weights = mc.parentConstraint(constraint_name, q=True, weightAliasList=True)

        # Connect fkIkSwitch attribute to constraint weights
        # fk weight = 1 - fkIkSwitch
        # ik weight = fkIkSwitch

        fk_weight_attr = f"{constraint_name}.{weights[0]}"
        ik_weight_attr = f"{constraint_name}.{weights[1]}"

        # Create a reverse node to invert the fkIkSwitch for FK weight
        rev_node = mc.createNode('reverse', name=f"{constraint_name}_rev")

        # Connect fkIkSwitch to reverse node inputX
        mc.connectAttr(f"{root_ctrl}.fkIkSwitch", f"{rev_node}.inputX", force=True)

        # Connect reverse outputX to FK weight
        mc.connectAttr(f"{rev_node}.outputX", fk_weight_attr, force=True)

        # Connect fkIkSwitch directly to IK weight
        mc.connectAttr(f"{root_ctrl}.fkIkSwitch", ik_weight_attr, force=True)

def build_chain_fkik_rig(rig_prefix='chain', rig_size=1.0, auto_skin=False, clear_guide=False):
    """
    Builds a 3-chain FK/IK rig with a switch on the Root_CTRL:
    - FK chain (with controls)
    - IK chain (with IK handle + control)
    - Bind chain (deforming mesh)
    """

    # === Step 1: Find Guide Locators ===
    all_guides = mc.ls(f'chain_guide_*', type='transform') or []

    def extract_index(name):
        match = re.search(rf'chain_guide_(\d+)', name)
        return int(match.group(1)) if match else -1

    sorted_guides = sorted(all_guides, key=extract_index)
    if not sorted_guides:
        mc.error(f"No guides found matching pattern: chain_guide_XX")

    # === Step 2: Create FK/IK Switch Attribute on Root_CTRL ===
    root_ctrl = f'{rig_prefix}_Root_CTRL'
    if not mc.objExists(root_ctrl):
        build_basic_control(
            name=f'{rig_prefix}_Root',
            size=5 * rig_size,
            color_rgb=(1, 0.5, 0.01),
            position=[0, 0, 0],
            rotation=[0, 0, 0]
        )

    if not mc.attributeQuery('fkIkSwitch', node=root_ctrl, exists=True):
        mc.addAttr(root_ctrl, longName='fkIkSwitch', attributeType='bool', keyable=True)

    #Step 3

    fk_joints = []
    ik_joints = []
    created_joints = []
    previous_ctrl = None

    for i, guide in enumerate(sorted_guides, 1):
        # Get guide transform
        pos = mc.xform(guide, q=True, t=True, ws=True)
        rot = mc.xform(guide, q=True, ro=True, ws=True)

        ctrl_name = f'{rig_prefix}_{str(i).zfill(2)}'
        jnt_name = f'{ctrl_name}_jnt'

        # Create control
        build_basic_control(
            name=f'{ctrl_name}_FK',
            size=2 * rig_size,
            color_rgb=(0.3, 0.7, 1),  # Cyan color for chain
            position=pos,
            rotation=rot
        )

        # Create joint
        mc.select(clear=True)
        jnt = mc.joint(p=pos, name=f'{ctrl_name}_bind_jnt')
        mc.joint(jnt, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        mc.makeIdentity(jnt, apply=True, t=1, r=1, s=1, n=0)
        created_joints.append(jnt)

        mc.select(clear=True)
        jnt = mc.joint(p=pos, name=f'{ctrl_name}_IK_jnt')
        mc.joint(jnt, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        mc.makeIdentity(jnt, apply=True, t=1, r=1, s=1, n=0)
        ik_joints.append(jnt)

        mc.select(clear=True)
        jnt = mc.joint(p=pos, name=f'{ctrl_name}_FK_jnt')
        mc.joint(jnt, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        mc.makeIdentity(jnt, apply=True, t=1, r=1, s=1, n=0)
        fk_joints.append(jnt)

        # Parent constraints
        mc.parentConstraint(f"{ctrl_name}_FK_CTRL", jnt, mo=False)
        mc.scaleConstraint(f"{ctrl_name}_FK_CTRL", jnt, mo=False)

        # Parent FK hierarchy
        if previous_ctrl:
            mc.parent(f"{ctrl_name}_FK_GRP", f"{previous_ctrl}_FK_CTRL")
            mc.parent(f"{ctrl_name}_bind_jnt", f"{previous_ctrl}_bind_jnt")
            mc.parent(f"{ctrl_name}_FK_jnt", f"{previous_ctrl}_FK_jnt")
            mc.parent(f"{ctrl_name}_IK_jnt", f"{previous_ctrl}_IK_jnt")
        previous_ctrl = ctrl_name

    #step 4
    # 1. Create the IK spline handle and IK control
    ik_ctrl_name, ik_curve_name = create_ik_spline_handle_and_control(ik_joints, rig_prefix, rig_size)
    print(f"Created IK Control: {ik_ctrl_name}, IK Curve: {ik_curve_name}")

    # 2. Create CV controls to manipulate the IK spline curve's CVs
    cv_ctrls, cv_controls_grp = add_ik_spline_cv_controls(ik_curve_name, rig_prefix, rig_size)
    print(f"Created {len(cv_ctrls)} CV controls under group: {cv_controls_grp}")

    # 3. Add twist controls on your root control (make sure this exists)
    root_ctrl_name = f'{rig_prefix}_Root_CTRL'  # Replace with your actual root control name if different
    #add_ik_spline_twist_controls(root_ctrl_name)
    print(f"Added twist attributes on: {root_ctrl_name}")

    make_ik_spline_stretchy(rig_prefix, ik_curve_name, ik_joints, f'{rig_prefix}_Root_CTRL')


    add_fkik_switch_and_blend(fk_joints, ik_joints, created_joints, rig_prefix)
    if auto_skin:
            main_jnt = created_joints
            model_grp = 'MODEL'
            
            # Get all geometry under MODEL, including nested children
            geo_list = mc.listRelatives(model_grp, allDescendents=True, type='mesh', fullPath=False) or []

            # Convert mesh shape nodes to transform nodes (geometry group)
            geo_transforms = list({mc.listRelatives(mesh, parent=True, fullPath=True)[0] for mesh in geo_list})

            # Bind each geo to the main joint
            for geo in geo_transforms:
                try:
                    mc.select([geo] + main_jnt)
                    mc.skinCluster(toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1, weightDistribution=0)
                except Exception as e:
                    print(f"Failed to skin {geo}: {e}")

    mc.parent(f'{rig_prefix}_01_FK_GRP', f'{rig_prefix}_Main_CTRL')
    for d in [f'{rig_prefix}_IK_GRP', f'{rig_prefix}_ikSpline_cv1_clusterHandle', f'{rig_prefix}_ikSpline_cv2_clusterHandle', f'{rig_prefix}_ikSpline_cv3_clusterHandle', f'{rig_prefix}_ikSpline_cv4_clusterHandle' ]:
        mc.hide(d)
    mc.parent(f'{rig_prefix}_IK_GRP', 'RIG')
    mc.parent(f'{rig_prefix}_IKSpline_CV_CTRLS_GRP', f'{rig_prefix}_Main_CTRL')
    #mc.parent(f'{rig_prefix}_01_jnt', f'{rig_prefix}_main_jnt')
    # Assume you have lists of your ik joints and fk joints/control groups
    ik_vis_objs = f'{rig_prefix}_IKSpline_CV_CTRLS_GRP'  # include your IK spline CV controls group if you want
    fk_vis_objs = f'{rig_prefix}_01_FK_GRP'  # your FK joints or controls groups
    for j in [f'{rig_prefix}_01_bind_jnt', f'{rig_prefix}_01_IK_jnt', f'{rig_prefix}_01_FK_jnt' ]:
        mc.parent(j, f'{rig_prefix}_main_jnt')



    connect_ik_spline_channels_to_main_ctrl(rig_prefix, f'{rig_prefix}_ikSplineHandle', f'{rig_prefix}_Main_CTRL')

    connect_visibility_to_fkik_switch(root_ctrl=f'{rig_prefix}_Root_CTRL',
                                    fkik_attr='fkIkSwitch',
                                    ik_objects=ik_vis_objs,
                                    fk_objects=fk_vis_objs)
    if clear_guide == True:
        mc.delete(sorted_guides)
    print("✔ Chain FK/IK rig created with FK/IK switch.")



def build_simple_prop_rig(
        geo_grp_name: str,
        pivot: str = 'origin',
        rig_size: float = 1,
        zootools: bool = True,
        keep_rig: bool = False,
        rig_prefix: str = "TEMP",
        auto_skin: bool = True,
        keep_rig_geo: bool = True,
        clear_cache: bool = False,
        clear_guide: bool = False,
    ):
    """
    builds simple prop rigs

    Args:
        geo_grp_name = once all of the geo is in a grp, just speciy the name of the group
        pivot: 'origin', 'guide', or 'center' origin will put the control at world origin, guide will take in a locator called "MainControl_guide" and place the control there,
            then if i get it working center will try and find the center of mass, to build the control on 
        rig_size: determins the visual size of the contorls, it is just a multiplier to the default size of the controls
        zootools: weather or not you are running zootools / can use their control building scripts
        keep_rig: if the usd rig structure pre-exists, this deterims if the script will either kill the old one, or error out
        rig_prefix = name the rig
        auto_skin = autoskins or it doesnt


    """
    ### --- ###
    """
    Suto Code
        First we need to check and see if the rig structure exists, if it does, following our args we kill it or error out
        Next check on the the geo grp
        next if we are using the guide method, we need to check if the guide is in the scene
        next we will want to build the usd rig structure
        then we will want to place our main jnt and contols based on our methood
        then we will want to take the contents of the geo group and deposit them, into the geo group in the USD build
        if autoskin will will want to skin all of the geo to our new joint
        last we will want to build our cache selection set  
    """

     # Check if 'ROOT' exists in the scene
    if mc.objExists("ROOT"):
        if keep_rig:
            mc.error('"ROOT" already exists in the scene and keep_rig is set to True.')
        else:
            if keep_rig_geo:
                model_grp = 'MODEL'
                if mc.objExists(model_grp):
                    # Check if the geo group exists, if not create it
                    if not mc.objExists(geo_grp_name):
                        geo_grp = mc.group(em=True, name=geo_grp_name)
                    else:
                        geo_grp = geo_grp_name

                    # Get children of MODEL group
                    children = mc.listRelatives(model_grp, children=True, fullPath=True) or []

                    # Parent each child to the geo group
                    for child in children:
                        mc.parent(child, geo_grp)
            mc.delete("ROOT")

     # --- Step 2: Check if geo group exists ---
    if not mc.objExists(geo_grp_name):
        mc.error(f'Geometry group "{geo_grp_name}" does not exist in the scene.')

     # --- Step 3: If using guide, check if the guide exists ---
    if pivot == 'guide':
        if not mc.objExists("MainControl_guide"):
            mc.error('Pivot mode is set to "guide", but "MainControl_guide" does not exist in the scene.')

     # --- Step 4: Build USD rig hierarchy ---

    # Create top-level groups
    root_grp = mc.group(em=True, name='ROOT')
    model_grp = mc.group(em=True, name='MODEL', parent=root_grp)
    rig_grp = mc.group(em=True, name='RIG', parent=root_grp)
    skel_grp = mc.group(em=True, name='SKEL', parent=root_grp)

    # Create the root joint under SKEL
    root_joint = mc.joint(name='root_jnt')
    mc.parent(root_joint, skel_grp)
    mc.makeIdentity(root_joint, apply=True, t=1, r=1, s=1, n=0)  # Freeze transforms

    # --- Step 5: Move geo into MODEL and delete old group ---
    geo_children = mc.listRelatives(geo_grp_name, children=True, fullPath=True) or []
    if geo_children:
        mc.parent(geo_children, model_grp)
    else:
        print(f" Warning: '{geo_grp_name}' has no children to move.")

    mc.delete(geo_grp_name)

    # --- Step 6: Handle pivot logic ---
    if pivot == 'origin':
        MainControlPos = [0, 0, 0]
        MainControlRot = [0, 0, 0]
    elif pivot == 'guide':
        MainControlPos = mc.xform('MainControl_guide', q=True, t=True, ws=True)
        MainControlRot = mc.xform('MainControl_guide', q=True, ro=True, ws=True)
    elif pivot == 'center':
        #mc.error('Ha, you thought Steve was smart enough to figure this part out')
            MainControlPos = get_model_center('MODEL')
            MainControlRot = [0, 0, 0]  # Usually we assume neutral rotation for center placement
    elif pivot == 'roll':
         MainControlPos = [0, 0, 0]
         MainControlRot = [0, 0, 0]
    elif pivot == 'simplechain':
         MainControlPos = [0, 0, 0]
         MainControlRot = [0, 0, 0]
    elif pivot == 'chain':
         MainControlPos = [0, 0, 0]
         MainControlRot = [0, 0, 0]
    elif pivot == 'cluster':
        MainControlPos = [0,0,0]
        MainControlRot = [0,0,0]
    else:
        mc.error('Pivot not set correctly in the arguments. Defaulting to "origin".')
        MainControlPos = [0, 0, 0]
        MainControlRot = [0, 0, 0]

    print(f"Main Control Position: {MainControlPos}, Rotation: {MainControlRot}")
    
    # --- Step 7: Build Controls ---
    # Build Root_CTRL
    build_basic_control(
        name=f'{rig_prefix}_Root',
        size=5 * rig_size,
        color_rgb=(1, 0.5, 0.01),
        position=(0, 0, 0),  # Positioned at the origin
        rotation=(0, 0, 0)   # No rotation
        )
    
    # Build Offset_CTRL
    build_basic_control(
        name=f'{rig_prefix}_Offset',
        size=4 * rig_size,  # 4 times the rig_size argument
        color_rgb=(0.95, 0.63, 0.37),  # #f2a15f in RGB
        position=(0, 0, 0),  # Positioned at the origin
        rotation=(0, 0, 0)   # No rotation
    )

    # === Build Main Control ===
    build_basic_control(
        name=f'{rig_prefix}_Main',  # Name with rig_prefix
        size=3 * rig_size,  # 3 times the rig_size argument
        color_rgb=(0.90, 0.38, 0.34),  # #e66057 in RGB
        position=MainControlPos,  # Use the calculated position
        rotation=MainControlRot   # Use the calculated rotation
    )

    # === Parent Controls ===
    mc.parent(f'{rig_prefix}_Offset_GRP', f'{rig_prefix}_Root_CTRL')  # Parent Offset_CTRL under Root_CTRL
    mc.parent(f'{rig_prefix}_Main_GRP', f'{rig_prefix}_Offset_CTRL')  # Parent Main_CTRL under Offset_CTRL
    mc.parent(f'{rig_prefix}_Root_GRP', 'RIG')

    # === Create Main Joint ===
    # Create the joint at the MainControlPos
    main_jnt = mc.joint(p=MainControlPos, orientation=MainControlRot)
    main_jnt = mc.rename(main_jnt, f'{rig_prefix}_main_jnt')
    mc.parent(main_jnt, 'root_jnt')

    # Set the joint's orientation (based on MainControlRot)
    #mc.joint(f'{rig_prefix}_main_jnt', edit=True, orientation=MainControlRot)

    # Constrain root joint to root control
    mc.parentConstraint(f"{rig_prefix}_Root_CTRL", f"root_jnt", mo=False)
    mc.scaleConstraint(f"{rig_prefix}_Root_CTRL", f"root_jnt", mo=False)

    # Constrain main joint to main control
    mc.parentConstraint(f"{rig_prefix}_Main_CTRL", f"{rig_prefix}_main_jnt", mo=False)
    mc.scaleConstraint(f"{rig_prefix}_Main_CTRL", f"{rig_prefix}_main_jnt", mo=False)

    if auto_skin and pivot not in ['simplechain', 'chain', 'cluster']:
        main_jnt = f'{rig_prefix}_main_jnt'
        model_grp = 'MODEL'
        
        # Get all geometry under MODEL, including nested children
        geo_list = mc.listRelatives(model_grp, allDescendents=True, type='mesh', fullPath=False) or []

        # Convert mesh shape nodes to transform nodes (geometry group)
        geo_transforms = list({mc.listRelatives(mesh, parent=True, fullPath=True)[0] for mesh in geo_list})

        # Bind each geo to the main joint
        for geo in geo_transforms:
            try:
                mc.select([geo, main_jnt])
                mc.skinCluster(toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1, weightDistribution=0)
            except Exception as e:
                print(f"Failed to skin {geo}: {e}")
    cache_set_name = 'cache_SET'

    # Check if cache_SET already exists
    if mc.objExists(cache_set_name):
        if not clear_cache:
            mc.error("Cache Set Already Exists")
        else:
            mc.delete(cache_set_name)
            mc.sets("MODEL", name=cache_set_name)
    else:
        # Create the new selection set
        mc.sets("MODEL", name=cache_set_name)

    #Hide Skel
    mc.setAttr('SKEL.visibility', 0)

    #Clear Guide
    if clear_guide and mc.objExists("MainControl_guide"):
        mc.delete("MainControl_guide")

    #Display Layers
    create_display_layer("MODEL_Display", "MODEL", 13, is_reference=True)  # Yellow and reference
    #create_display_layer("RIG_Display", "RIG", 0)       # Blue
    #create_display_layer("SKEL_Display", "SKEL", 20)    # Purple
    if pivot == 'roll':
        build_roll_rig(rig_prefix, rig_size)
    if pivot == 'simplechain':
        build_simplechain_rig(rig_prefix, rig_size, auto_skin, clear_guide)
    if pivot == 'chain':
        build_chain_fkik_rig(rig_prefix, rig_size, auto_skin, clear_guide)
    if pivot == 'cluster':
        build_simplecluster_rig(rig_prefix, rig_size, auto_skin, clear_guide)


class SimplePropAutoRiggerUI(QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super().__init__(parent)
        self.setWindowTitle("Simple Prop Auto Rigger")
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.build_ui()
        self.create_connections()

    def build_ui(self):
        # Widgets
        self.geo_input = QtWidgets.QLineEdit()
        self.prefix_input = QtWidgets.QLineEdit()
        self.rig_size_input = QtWidgets.QDoubleSpinBox()
        self.rig_size_input.setValue(2.0)
        self.rig_size_input.setSingleStep(0.1)
        self.rig_size_input.setMinimum(0.0)

        self.pivot_dropdown = QtWidgets.QComboBox()
        self.pivot_dropdown.addItems(["center", "guide", "origin", "roll", "simplechain", "chain", "cluster"])

        self.auto_skin_checkbox = QtWidgets.QCheckBox("Auto Skin")
        self.clear_cache_checkbox = QtWidgets.QCheckBox("Clear Cache")
        self.clear_guide_checkbox = QtWidgets.QCheckBox("Clear Guide")

        self.build_guides_button = QtWidgets.QPushButton("Build Guides")

        self.build_button = QtWidgets.QPushButton("Build Rig")

        # Layouts
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Geo Group Name:", self.geo_input)
        form_layout.addRow("Pivot:", self.pivot_dropdown)
        form_layout.addRow("Rig Size:", self.rig_size_input)
        form_layout.addRow("Rig Prefix:", self.prefix_input)
        form_layout.addRow(self.auto_skin_checkbox)
        form_layout.addRow(self.clear_cache_checkbox)
        form_layout.addRow(self.clear_guide_checkbox)
        form_layout.addRow(self.build_guides_button)
        form_layout.addRow(self.build_button)

        self.setLayout(form_layout)

    def create_connections(self):
        self.build_button.clicked.connect(self.run_rig_function)
        self.build_guides_button.clicked.connect(self.run_build_guides)
    
    def run_build_guides(self):
        pivot = self.pivot_dropdown.currentText()
        build_guides(pivot)

    def run_rig_function(self):
        geo_name = self.geo_input.text()
        pivot = self.pivot_dropdown.currentText()
        rig_size = self.rig_size_input.value()
        rig_prefix = self.prefix_input.text()
        auto_skin = self.auto_skin_checkbox.isChecked()
        clear_cache = self.clear_cache_checkbox.isChecked()
        clear_guide = self.clear_guide_checkbox.isChecked()

        build_simple_prop_rig(
            geo_grp_name=geo_name,
            pivot=pivot,
            rig_size=rig_size,
            rig_prefix=rig_prefix,
            auto_skin=auto_skin,
            clear_cache=clear_cache,
            clear_guide=clear_guide
        )



def show_simple_prop_rigger():
    global simple_prop_rigger_win
    try:
        simple_prop_rigger_win.close()
        simple_prop_rigger_win.deleteLater()
    except:
        pass

    simple_prop_rigger_win = SimplePropAutoRiggerUI()
    simple_prop_rigger_win.show()

show_simple_prop_rigger()



#build_simple_prop_rig(geo_grp_name='test_grp', pivot='center', rig_size = 2, zootools = True, rig_prefix='Cubes', auto_skin=True, clear_cache=True, clear_guide=True )