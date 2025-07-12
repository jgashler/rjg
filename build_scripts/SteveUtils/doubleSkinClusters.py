import maya.cmds as mc
import re

def get_selected_list():
    selection_list = []
    selection = mc.ls(selection=True)
    for obj in selection:
        selection_list.append(obj)
    return selection_list

def get_selected_with_suffix(suffix='_ctrl'):
    """
    Returns short names of selected objects whose names end with the given suffix.

    Args:
        suffix (str): The suffix to filter by (e.g., '_ctrl')

    Returns:
        list[str]: List of short names that match
    """
    matched = []
    selection = mc.ls(selection=True, long=True)

    for obj in selection:
        short_name = obj.split('|')[-1]
        if short_name.endswith(suffix):
            matched.append(short_name)

    return matched

def get_parents_from_list(obj_list):
    """
    Returns a dictionary mapping each object to its parent (or None if unparented).

    Args:
        obj_list (list[str]): List of object names

    Returns:
        dict[str, str or None]: Mapping of object → parent
    """
    parent_map = {}

    for obj in obj_list:
        parent = mc.listRelatives(obj, parent=True, fullPath=False)
        parent_map[obj] = parent[0] if parent else None

    return parent_map

def get_jnts(controls_list, ctrl_suffix="_ctrl", jnt_suffix="_jnt"):
    joint_list = []
    for ctrl in controls_list:
        short_name = ctrl

        if not short_name.endswith(ctrl_suffix):
            mc.warning(f"Skipped: {short_name} does not end with expected suffix '{ctrl_suffix}'")
            continue

        # Replace suffix to get joint name
        joint_name = short_name.replace(ctrl_suffix, jnt_suffix)

        # Check if joint exists by short name
        joint = mc.ls(joint_name, type="joint")
        if not joint:
            mc.warning(f"Joint not found for control: {short_name} → {joint_name}")
            continue

        joint_list.append(joint[0])
    return joint_list


def preview_bind_pre_matrix_connections(joints, offset_suffix='_grp', joint_suffix='_jnt', ctrl_suffix='_ctrl'):
    """
    Finds each joint's skinCluster and prints the intended worldInverseMatrix → bindPreMatrix connections.

    Args:
        joints (list[str]): List of joint names
        offset_suffix (str): Suffix for control offset group
        joint_suffix (str): Suffix to strip from joint name
        ctrl_suffix (str): Suffix to append for control name
    """
    print("\n--- Matrix Connection Preview ---")

    for joint in joints:
        # Validate joint name
        if not joint.endswith(joint_suffix):
            print(f"[!] {joint} does not end with '{joint_suffix}' — skipped.")
            continue

        # Find connected skinCluster
        connections = mc.listConnections(f"{joint}.worldMatrix[0]", destination=True, source=False, type='skinCluster') or []
        if not connections:
            print(f"[!] No skinCluster connected to {joint} — skipped.")
            continue

        skin_cluster = connections[0]

        # Get index in skinCluster
        influences = mc.skinCluster(skin_cluster, q=True, inf=True)
        if joint not in influences:
            print(f"[!] {joint} not listed in {skin_cluster} influences — skipped.")
            continue

        index = influences.index(joint)

        # Derive offset group
        base = joint.replace(joint_suffix, '')
        ctrl = f"{base}{ctrl_suffix}"
        offset_grp = f"{base}{offset_suffix}"

        if not mc.objExists(offset_grp):
            print(f"[!] Offset group not found: {offset_grp} — skipped.")
            continue

        # Print intended connection
        src_attr = f"{offset_grp}.worldInverseMatrix[0]"
        dest_attr = f"{skin_cluster}.bindPreMatrix[{index}]"

        print(f"[✓] {joint}:")
        print(f"     SkinCluster: {skin_cluster}")
        print(f"     Offset Group: {offset_grp}")
        print(f"     Index: {index}")
        print(f"     {src_attr} → {dest_attr}")

    print("--- End Preview ---\n")

#joints = mc.ls(sl=True, type='joint')
#preview_bind_pre_matrix_connections(joints)





def connect_double():
    geo = 'FaceAtOrigin'
    controls = get_selected_with_suffix(suffix='_ctrl')
    offsets = get_parents_from_list(controls)
    jnts = get_jnts(controls, ctrl_suffix="_ctrl", jnt_suffix="_jnt")


    # UV Pin all offset groups to the source geo
    if not mc.objExists(geo):
        mc.error(f"Source geometry '{geo}' does not exist.")
        return

    # Select source geo and then all the offset groups
    mc.select(clear=True)
    mc.select(geo)
    mc.select(offsets, add=True)
    pinnode = mc.UVPin()
    
    for offset_name in offsets:
        if mc.objExists(offset_name):
            mc.setAttr(f"{offset_name}.translate", 0, 0, 0)
            mc.setAttr(f"{offset_name}.rotate", 0, 0, 0)
            mc.setAttr(f"{offset_name}.scale", 1, 1, 1)
    
    print(f"UV Pin Node created: {pinnode}")

    history = mc.listHistory(geo, pruneDagObjects=True) or []
    deformer_types = ["skinCluster", "blendShape", "lattice", "wrap", "cluster"]

    # Iterate in order to get the first (oldest) deformer
    for node in history:
        if mc.nodeType(node) in deformer_types:
            topofthestack = node
            break
    
    ## -- get the pin node name -- ##
    all_nodes = mc.ls(type="uvPin")  # Filter by uvPin type
    uvpin_nodes = []
    for node in all_nodes:
        match = re.match(r'^uvPin(\d+)$', node)
        if match:
            uvpin_nodes.append((node, int(match.group(1))))

    if not uvpin_nodes:
        mc.warning("No uvPin nodes found with numeric suffix.")
        return None

    # Find the node with the highest number
    highest_node = max(uvpin_nodes, key=lambda x: x[1])[0]
    pinname = highest_node



    # Get the output geometry plug from the top deformer
    deformer_output = f"{topofthestack}.outputGeometry[0]"

    # Get the input plug on the UVPin node
    uvpin_input = f"{pinname}.deformedGeometry"

    mc.connectAttr(deformer_output, uvpin_input, force=True)

    #Inverse Matrix Math
    for i, guide in enumerate(offsets):
        number = guide.split('_')[-1]
        offset_grp = f"{GuidePrefix}_curvenet_{number}_grp"
        src_attr = f"{offset_grp}.worldInverseMatrix[0]"
        dest_attr = f"curve_net_skin_cluster.bindPreMatrix[{i}]"
        mc.connectAttr(src_attr, dest_attr, force=True)