import maya.cmds as mc

def uv_pin_ribbon_group(rib_group):
    # Extract the base name from the given RIB group name (assumes format 'NAME_RIBgrp')
    base_name = rib_group.replace("_RIBgrp", "")
    
    # Define the ribbon object name
    ribbon_object = f"{base_name}_ribbon"
    
    # Get the child objects in the group
    children = mc.listRelatives(rib_group, children=True) or []
    
    # Filter objects that have the suffix "_grp"
    ctrl_pins = [obj for obj in children if obj.endswith("_grp")]
    
    # Sort the groups numerically (if they have _PIN_##_grp format)
    ctrl_pins.sort(key=lambda x: int(x.split("_")[-2]))  

    # Determine the number of groups
    num_pins = len(ctrl_pins)
    
    # Generate the pin locations list (normalized values between 0 and 1)
    pin_locations = [i / float(num_pins - 1) for i in range(num_pins)]
    
    # List to store world-space positions
    pin_positions = []

    # Get the world-space positions of the pins using UV coordinates (U varies, V is 0.5)
    for u in pin_locations:
        position = mc.pointOnSurface(ribbon_object, position=True, parameterU=u, parameterV=0.5)
        pin_positions.append(position)

    # Generate a list for points (formatted like 'NAME_point##_cjnt')
    point_cjnts = [f"{base_name}_point{str(i+1).zfill(2)}_cjnt" for i in range(num_pins)]

    # Get the world position and world rotation (orientation) for each joint
    world_positions = []
    world_orientations = []
    
    for cjnt in point_cjnts:
        # Get world position using xform
        position = mc.xform(cjnt, q=True, ws=True, t=True)
        world_positions.append(position)
        
        # Get world orientation (rotation in world space)
        rotation = mc.xform(cjnt, q=True, ws=True, ro=True)
        world_orientations.append(rotation)

    # Now, match the world positions and rotations of the joints to the _grps
    for i, grp in enumerate(ctrl_pins):
        # Match corresponding cjnt's world position and orientation
        target_pos = world_positions[i]
        target_rot = world_orientations[i]
        
        # Apply the world position and orientation to the _grp
        mc.xform(grp, ws=True, t=target_pos)  # Set the world position
        mc.xform(grp, ws=True, ro=target_rot)  # Set the world orientation

    # Perform UV pinning on the Ribbon and _grps
    # Iterate through the control pin _grps and pin them to the Ribbon's surface
    for i, grp in enumerate(ctrl_pins):
        u_value = pin_locations[i]  # Use the corresponding U value from the pin locations
        v_value = 0.5  # Fixed V value for UV pinning

        # Pin the control pin (group) to the ribbon surface using UV coordinates
    mc.select(ribbon_object)  # Add ribbon object to selection
    mc.select(ctrl_pins, add=True)
    mc.UVPin()  # Pin the selected objects to the ribbon

    print("UV Pinning applied to Ribbon and _grps.")

    try:
        ribbon_object_clone = ribbon_object + "_clone"
        source_history = mc.listHistory(ribbon_object_clone)
        source_skin = mc.ls(source_history, type="skinCluster")
        target_history = mc.listHistory(ribbon_object_clone)
        #target_skin = mc.ls(target_history, type="skinCluster")
        influences = mc.skinCluster(source_skin, query=True, influence=True)
        target_skin = mc.skinCluster(influences, ribbon_object, toSelectedBones=True)[0]
        mc.copySkinWeights(
        ss=source_skin[0],
        ds=target_skin[0],
        noMirror=True,
        surfaceAssociation="closestPoint",)
    except Exception as e:
        print(e)

# Example Usage
rib_group = "TEST_RIBgrp"  # Replace with your actual RIB group name
uv_pin_ribbon_group(rib_group)
