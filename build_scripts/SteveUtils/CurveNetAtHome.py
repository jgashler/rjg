import maya.cmds as mc
import re

def uv_pin (
        object_to_pin: str, 
        surface: str, 
        u: float = 0, 
        v: float = 0,
        local_space: bool = False,
        normalize: bool = False,
        normal_axis: str = None,
        tangent_axis: str = None,
        reset_transforms: bool = True,
) -> str:
    """
    Create a UVPin node that pins an object to a given surface at specified UV coordinates.

    Args:
        object_to_pin: The name of the object to be pinned.
        surface: The name of the surface (mesh or NURBS) to pin to.
        u: The U coordinate.
        v: The V coordinate.
        local_space: When true, sets UVPin node to local relativeSpaceMode. When false, the pinned object has inheritsTransform disabled to prevent double transforms.
        normalize: Enable Isoparm normalization (NURBS UV will be remapped between 0-1).
        normal_axis: Normal axis of the generated uvPin, can be x y z -x -y -z.
        tangent_axis: Tangent axis of the generated uvPin, can be x y z -x -y -z.
        reset_transforms: When True, reset the pinned object's transforms.
    Returns:
        The name of the created UVPin node.
    """
    # Retrieve shape nodes from the surface.
    shapes = mc.listRelatives(surface, children=True, shapes=True) or []
    if not shapes:
        mc.error(f"No shape nodes found on surface: {surface}")
    
    # Choose the primary shape (non-intermediate if available) and check for an existing intermediate shape.
    primary_shape = next((s for s in shapes if not mc.getAttr(f"{s}.intermediateObject")), shapes[0])
    shape_origin = next((s for s in shapes if mc.getAttr(f"{s}.intermediateObject")), None) 

    # Determine attribute names based on surface type.
    surface_type = mc.objectType(primary_shape)
    if surface_type == "mesh":
        attr_input = ".inMesh"
        attr_world = ".worldMesh[0]"
        attr_output = ".outMesh"
    elif surface_type == "nurbsSurface":
        attr_input = ".create"
        attr_world = ".worldSpace[0]"
        attr_output = ".local"
    else:
        mc.error(f"Unsupported surface type: {surface_type}")

    # If no intermediate shape exists, create one.
    if shape_origin is None:
        duplicated = mc.duplicate(primary_shape)[0]
        shape_origin_list = mc.listRelatives(duplicated, children=True, shapes=True)
        if not shape_origin_list:
            mc.error("Could not create intermediate shape.")
        shape_origin = shape_origin_list[0]
        mc.parent(shape_origin, surface, shape=True, relative=True)
        mc.delete(duplicated)
        new_name = f"{primary_shape}Orig"
        shape_origin = mc.rename(shape_origin, new_name)
        # If there is an incoming connection, reconnect it.
        in_conn = mc.listConnections(f"{primary_shape}{attr_input}", plugs=True, connections=True, destination=True)
        if in_conn:
            mc.connectAttr(in_conn[1], f"{shape_origin}{attr_input}")
        mc.connectAttr(f"{shape_origin}{attr_world}", f"{primary_shape}{attr_input}", force=True)
        mc.setAttr(f"{shape_origin}.intermediateObject", 1)
    
    # Create the UVPin node and connect it.
    uv_pin = mc.createNode("uvPin", name=f"{object_to_pin}_uvPin")
    mc.connectAttr(f"{primary_shape}{attr_world}", f"{uv_pin}.deformedGeometry")
    mc.connectAttr(f"{shape_origin}{attr_output}", f"{uv_pin}.originalGeometry")
    mc.xform(object_to_pin, translation=[0, 0, 0], rotation=[0, 0, 0])
    
    if normal_axis:
        if normal_axis == "x":
            mc.setAttr(f"{uv_pin}.normalAxis", 0)
        elif normal_axis == "y":
            mc.setAttr(f"{uv_pin}.normalAxis", 1)
        elif normal_axis == "z":
            mc.setAttr(f"{uv_pin}.normalAxis", 2)
        elif normal_axis == "-x":
            mc.setAttr(f"{uv_pin}.normalAxis", 3)
        elif normal_axis == "-y":
            mc.setAttr(f"{uv_pin}.normalAxis", 4)
        elif normal_axis == "-z":
            mc.setAttr(f"{uv_pin}.normalAxis", 5)
        else:
            raise RuntimeError(f"{normal_axis} isn't a valid axis, it should be x y z -x -y -z")
    else:
        mc.setAttr(f"{uv_pin}.normalAxis", 1)

    if tangent_axis:
        if tangent_axis == "x":
            mc.setAttr(f"{uv_pin}.tangentAxis", 0)
        elif tangent_axis == "y":
            mc.setAttr(f"{uv_pin}.tangentAxis", 1)
        elif tangent_axis == "z":
            mc.setAttr(f"{uv_pin}.tangentAxis", 2)
        elif tangent_axis == "-x":
            mc.setAttr(f"{uv_pin}.tangentAxis", 3)
        elif tangent_axis == "-y":
            mc.setAttr(f"{uv_pin}.tangentAxis", 4)
        elif tangent_axis == "-z":
            mc.setAttr(f"{uv_pin}.tangentAxis", 5)
        else:
            raise RuntimeError(f"{tangent_axis} isn't a valid axis, it should be x y z -x -y -z")
    else:
        mc.setAttr(f"{uv_pin}.tangentAxis", 0)
    

    mc.setAttr(f"{uv_pin}.normalizedIsoParms", 0)
    mc.setAttr(f"{uv_pin}.coordinate[0]", u, v, type="float2")
    mc.connectAttr(f"{uv_pin}.outputMatrix[0]", f"{object_to_pin}.offsetParentMatrix")

    if normalize:
        mc.setAttr(f"{uv_pin}.normalizedIsoParms", 1)

    if local_space:
        mc.setAttr(f"{uv_pin}.relativeSpaceMode", 1)
    else:
        mc.setAttr(f"{object_to_pin}.inheritsTransform", 0)
    return uv_pin

def consolidate_uvpins() -> None:
    uv_pin_nodes = mc.ls(type="uvPin")
    uv_pin_dict = {}
    for uv_pin_node in uv_pin_nodes:
        try:
            input_geo: tuple = (mc.listConnections(f"{uv_pin_node}.originalGeometry", source=True, plugs=True)[0], mc.listConnections(f"{uv_pin_node}.deformedGeometry", source=True, plugs=True)[0])
        except: 
            continue
        connections = mc.listConnections(f"{uv_pin_node}", connections=True, plugs=True)
        attributes = mc.listAttr(f"{uv_pin_node}", multi=True)
        attribute_values = []
        for attribute in attributes:
            if attribute in ["uvSetName", "normalOverride", "railCurve", "normalAxis", "tangentAxis", "normalizedIsoParms", "relativeSpaceMode", "relativeSpaceMatrix"]:
                attribute_values.append((attribute, mc.getAttr(f"{uv_pin_node}.{attribute}")))
            if "coordinateU" in attribute:
                attribute_values.append((attribute, mc.getAttr(f"{uv_pin_node}.{attribute}")))
            if "coordinateV" in attribute:
                attribute_values.append((attribute, mc.getAttr(f"{uv_pin_node}.{attribute}")))
        if input_geo in uv_pin_dict:
            uv_pin_dict[input_geo].append((connections, attribute_values))
        else:
            uv_pin_dict[input_geo] = [(connections, attribute_values)]
    for input_geo, connections_attributes in uv_pin_dict.items():
        uv_pin = mc.createNode("uvPin", name=f"{input_geo[1]}_uvPin".replace("Shape.worldSpace", "_master"))
        mc.connectAttr(input_geo[0], f"{uv_pin}.originalGeometry")
        mc.connectAttr(input_geo[1], f"{uv_pin}.deformedGeometry")
        pin_num: int = 0 
        for attribute_value in connections_attributes[0][1]:
            if attribute_value[0] == "uvSetName":
                mc.setAttr(f"{uv_pin}.{attribute_value[0]}", attribute_value[1], type="string")
            if attribute_value[0] in ["relativeSpaceMode", "normalAxis", "tangentAxis", "normalOverride", "normalizedIsoParms"]:
                mc.setAttr(f"{uv_pin}.{attribute_value[0]}", attribute_value[1])
            if attribute_value[0] == "relativeSpaceMatrix":
                mc.setAttr(f"{uv_pin}.{attribute_value[0]}", attribute_value[1], type="matrix")
        
        for connection_attribute in connections_attributes:
            connections = connection_attribute[0]
            connection_pairs = list(zip(connections[0::2], connections[1::2]))
            u_map = {}
            v_map = {}
            for connection in connection_pairs:
                if "coordinateU" in connection[0]:
                    mc.disconnectAttr(connection[1], connection[0])
                    mc.connectAttr(connection[1], f"{uv_pin}.coordinate[{pin_num}].coordinateU")
                    u_map[pin_num] = True
                if "coordinateV" in connection[0]:
                    mc.disconnectAttr(connection[1], connection[0])
                    mc.connectAttr(connection[1], f"{uv_pin}.coordinate[{pin_num}].coordinateV")
                    v_map[pin_num] = True
                if "outputMatrix" in connection[0]:
                    mc.disconnectAttr(connection[0], connection[1])
                    mc.connectAttr(f"{uv_pin}.outputMatrix[{pin_num}]", connection[1])
            for attribute in connection_attribute[1]:
                if "coordinateU" in attribute[0]:
                    if pin_num not in u_map:
                        mc.setAttr(f"{uv_pin}.coordinate[{pin_num}].coordinateU", attribute[1])
                if "coordinateV" in attribute[0]:
                    if pin_num not in v_map:
                        mc.setAttr(f"{uv_pin}.coordinate[{pin_num}].coordinateV", attribute[1])      
            pin_num += 1
    for uv_pin_node in uv_pin_nodes:
        mc.delete(uv_pin_node)
            

#import maya.mc as mc

def create_curve_net_joints(GuidePrefix, SourceGeo):
    # Define the name of the guide group using the prefix
    group_name = f'{GuidePrefix}_CurveNetGuide'

    # Error out if the guide group doesn't exist
    if not mc.objExists(group_name):
        mc.error(f"Group '{group_name}' does not exist.")
        return

    # Get the direct children of the guide group (no full paths needed here)
    children = mc.listRelatives(group_name, children=True, fullPath=False) or []
    guide_joints = []

    # DEBUG: Print found children
    print(children)

    # Loop through children and filter for those that match the naming convention
    for obj in children:
        obj_name = obj.split('|')[-1]  # Get the short name

        # Must start with something like "TEST_CurveNet_Guide_1"
        if obj_name.startswith(f"{GuidePrefix}_CurveNet_Guide_"):
            guide_joints.append(obj)

    if not guide_joints:
        mc.warning("No valid guides found.")
        return

    # Define the name for the group to hold all generated joints
    def_grp_name = f"{GuidePrefix}_defpoints_grp"

    # Create the group if it doesn't already exist
    if not mc.objExists(def_grp_name):
        def_grp = mc.group(em=True, name=def_grp_name)
    else:
        def_grp = def_grp_name

    # Loop through all guide objects and create joints
    for guide in guide_joints:
        number = guide.split('_')[-1]  # Get the number suffix

        # Query world space position and rotation
        pos = mc.xform(guide, q=True, ws=True, t=True)
        rot = mc.xform(guide, q=True, ws=True, ro=True)

        # Create the joint name
        joint_name = f"{GuidePrefix}_curvenetpoint_{number}_jnt"

        # Skip if the joint already exists
        if mc.objExists(joint_name):
            mc.warning(f"Joint {joint_name} already exists. Skipping.")
            continue

        # Create the joint and apply the transforms
        jnt = mc.joint(name=joint_name)
        mc.xform(jnt, ws=True, t=pos, ro=rot)

        # Parent to the joint group
        mc.parent(jnt, def_grp)

    print(f"Created {len(guide_joints)} joints under {def_grp_name}.")

    # After joint creation, move on to controls
    
    ####################################################################

    # Look for the base template group and control
    if not mc.objExists("template_grp"):
        mc.error("template_grp does not exist in the scene.")
        return

    # Get position/rotation of the template_grp for duplicating later
    template_cont = "template_ctrl"
    template_grp = "template_grp"
    control_grp = []
    control_grp_name = mc.group(em=True, name=f'{GuidePrefix}_Controls_grp')
    for guide in guide_joints:
        number = guide.split('_')[-1]  # Get the guide number

        # Define names for the new duplicated control hierarchsy
        offset_name = f"{GuidePrefix}_curvenet_{number}_grp"
        control_name = f"{GuidePrefix}_curvenet_{number}_ctrl"

        # Duplicate the whole template group (including control inside)
        dup_cont = mc.duplicate(template_cont)[0]
        dup_grp = mc.duplicate(template_grp)[0]
        # Rename the internal control inside the duplicated group
        dup_cont = mc.rename(dup_cont, control_name)
        dup_grp = mc.rename(dup_grp, offset_name)
        mc.parent(dup_cont, dup_grp)
        mc.parent(dup_grp, control_grp_name)

        # Match the transform of the corresponding joint to the duplicated group
        joint_name = f"{GuidePrefix}_curvenetpoint_{number}_jnt"
        if mc.objExists(joint_name):
            pos = mc.xform(joint_name, q=True, ws=True, t=True)
            rot = mc.xform(joint_name, q=True, ws=True, ro=True)

            mc.xform(dup_grp, ws=True, t=pos, ro=rot)
        try:
            mc.parentConstraint(dup_cont, joint_name, mo=False)
            mc.scaleConstraint(dup_cont, joint_name, mo=False)
        except Exception as e:
            mc.warning(f"Could not constrain {joint_name} to {dup_grp}: {e}")
         

    
    ####
    ###UV Pin    
    ###Custon input
    ###Skincluster 2
    ###Inverse Matrix
    ###
    
    # ---------------- UV PINNING ----------------
    # Collect all offset groups
    offset_groups = []

    for guide in guide_joints:
        number = guide.split('_')[-1]
        offset_name = f"{GuidePrefix}_curvenet_{number}_grp"
        if mc.objExists(offset_name):
            offset_groups.append(offset_name)
    '''       
    for guide in guide_joints:
        number = guide.split('_')[-1]
        offset_name = f"{GuidePrefix}_curvenet_{number}_grp"
        print(offset_name)
        if mc.objExists(offset_name):
            mc.makeIdentity(offset_name, apply=True, translate=True, rotate=True, scale=True)
    '''

    # UV Pin all offset groups to the source geo
    if not mc.objExists(SourceGeo):
        mc.error(f"Source geometry '{SourceGeo}' does not exist.")
        return

    # Select source geo and then all the offset groups
    mc.select(clear=True)
    mc.select(SourceGeo)
    mc.select(offset_groups, add=True)
    pinnode = mc.UVPin()

    # Run UV pinning via MEL
    #print(offset_groups)
    #for guide in guide_joints:
    #    number = guide.split('_')[-1]
    #    offset_name = f"{GuidePrefix}_curvenet_{number}_grp"
    #    pinnode = uv_pin(object_to_pin=offset_name, surface=SourceGeo, normal_axis='y', tangent_axis='x', local_space=True, ) 
        
    # uvpin_result will be the name of the new uvPin node

    for guide in guide_joints:
        number = guide.split('_')[-1]
        offset_name = f"{GuidePrefix}_curvenet_{number}_grp"
        if mc.objExists(offset_name):
            mc.setAttr(f"{offset_name}.translate", 0, 0, 0)
            mc.setAttr(f"{offset_name}.rotate", 0, 0, 0)
            mc.setAttr(f"{offset_name}.scale", 1, 1, 1)

    
    print(f"UV Pin Node created: {pinnode}")
    
    ##-- Get last Deformer --#
    """
    Returns the first (base) deformer in the history stack for the given mesh.
    
    :param mesh: The name of the mesh object.
    :return: The first deformer node or None.
    """
    if not mc.objExists(SourceGeo):
        print(f"Error: Mesh '{SourceGeo}' does not exist.")
        return None

    history = mc.listHistory(SourceGeo, pruneDagObjects=True) or []
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
    
    #Bind second SkinCluster 

    # Check if the null joint exists, otherwise create it at world origin
    skin_cluster_name = "curve_net_skin_cluster"
    if mc.objExists(skin_cluster_name):
        # Rename the existing skin cluster
        new_name = f"{skin_cluster_name}_old"
        mc.rename(skin_cluster_name, new_name)
        print(f"Renamed existing skin cluster to {new_name}")

    if not mc.objExists('curve_net_null_joint'):
        NULL_Joint = mc.joint(name='curve_net_null_joint', p=(0, 0, 0))
        mc.setAttr(f"{NULL_Joint}.radius", 0.1)  # Set a small radius for visibility
    else:
        NULL_Joint = 'curve_net_null_joint'
    jnt_list = []
    for guide in guide_joints:
        number = guide.split('_')[-1]
        jnt_name = f"{GuidePrefix}_curvenetpoint_{number}_jnt"
        jnt_list.append(jnt_name)
    # Add the null joint to the joint list (make sure it's the last one)
    jnt_list.append(NULL_Joint)
    skin_cluster = mc.skinCluster(jnt_list, SourceGeo, toSelectedBones=True,multi=True, name="curve_net_skin_cluster")[0]

    #Inverse Matrix Math
    for i, guide in enumerate(guide_joints):
        number = guide.split('_')[-1]
        offset_grp = f"{GuidePrefix}_curvenet_{number}_grp"
        src_attr = f"{offset_grp}.worldInverseMatrix[0]"
        dest_attr = f"curve_net_skin_cluster.bindPreMatrix[{i}]"
        mc.connectAttr(src_attr, dest_attr, force=True)




    
    
    
    



   
#create_curve_net_joints('TEST', 'humanBody')


######## ---- ########
'''
The guides need to be names like so '{Prefix}_CurveNet_Guide_{Number}{Optionally side (L R etc)}'
The guide group needs to be named like so '{GuidePrefix}_CurveNetGuide'
then in the function set the frist argument to be the prefix then the second to your deforming object


'''