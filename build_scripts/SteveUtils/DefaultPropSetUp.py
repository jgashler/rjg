import maya.cmds as mc

import maya.cmds as mc

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

    if auto_skin:
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










build_simple_prop_rig(geo_grp_name='test_grp', pivot='center', rig_size = 2, zootools = True, rig_prefix='Cubes', auto_skin=True, clear_cache=True, clear_guide=True )