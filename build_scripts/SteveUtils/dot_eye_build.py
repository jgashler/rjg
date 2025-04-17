import maya.cmds as mc
import math
import rjg.post.dataIO.ng_weights as rWeightNgIO
import rjg.libs.util as rUtil

import sys
sys.path.append('/path/to/controls_directory')
#import controls
#groups = 'G:' if platform.system() == 'Windows' else '/groups'
groups = 'G:'

import rjg.build.rigModule as rModule
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.libs.attribute as rAttr

from importlib import reload
import platform, time

character = 'FaceAtOrigin'


'''
    Build Geo
    Buidl Skel
    Bind Skel
    place controls
    constrain conrtrols to bones  
    pull premade skin weights
    /groups/bobo/character/Rigs/DotEye
    pull premade shape library 
    connect shape targets with controls 
    set up parent constraint to geo (for now input will be a gui)

rCtrl.Control(parent=self.control_grp, shape='circle', side=self.side, suffix='CTRL', name=self.base_name, axis='z', group_type='main', rig_type='primary', translate=self.guide_list[0], rotate=(0, 0, 0), ctrl_scale=self.ctrl_scale)


fix remape to shape targets to ty instead of x

'''

#Calcualte Distances
def calc_vertical_eye(obj1, obj2):
    if not mc.objExists(obj1) or not mc.objExists(obj2):
        mc.warning(f"One or both objects ({obj1}, {obj2}) do not exist.")
        return None

    pos1 = mc.xform(obj1, query=True, worldSpace=True, translation=True)
    pos2 = mc.xform(obj2, query=True, worldSpace=True, translation=True)

    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    dz = pos2[2] - pos1[2]

    actual_distance = math.sqrt(dx**2 + dy**2 + dz**2)
    
    # Adjusted vertical angle calculation
    vertical_angle = - (math.degrees(math.atan2(dy, dz)) + 90)

    return [actual_distance, dx, dy, dz, vertical_angle]

def calc_horizontal_eye(obj1, obj2):
    if not mc.objExists(obj1) or not mc.objExists(obj2):
        mc.warning(f"One or both objects ({obj1}, {obj2}) do not exist.")
        return None

    pos1 = mc.xform(obj1, query=True, worldSpace=True, translation=True)
    pos2 = mc.xform(obj2, query=True, worldSpace=True, translation=True)

    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    dz = pos2[2] - pos1[2]

    actual_distance = math.sqrt(dx**2 + dy**2 + dz**2)

    # Adjusted horizontal angle calculation
    horizontal_angle = math.degrees(math.atan2(dx, dz)) - 90

    return [actual_distance, dx, dy, dz, horizontal_angle]

def calc_guide_thickness(obj1, obj2):
    if not mc.objExists(obj1) or not mc.objExists(obj2):
        mc.warning(f"One or both objects ({obj1}, {obj2}) do not exist.")
        return None

    pos1 = mc.xform(obj1, query=True, worldSpace=True, translation=True)
    pos2 = mc.xform(obj2, query=True, worldSpace=True, translation=True)

    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    dz = pos2[2] - pos1[2]

    actual_distance = math.sqrt(dx**2 + dy**2 + dz**2)
    return actual_distance

def calc_guide_center():
    """Finds the center point of all six guide objects."""
    guides = ["L_EyeGuideTop", "L_EyeGuideBot", "L_EyeGuideIn", "L_EyeGuideOut", "L_EyeGuide_Back", "L_EyeGuide_Front"]
    positions = []

    for guide in guides:
        if mc.objExists(guide):
            positions.append(mc.xform(guide, query=True, worldSpace=True, translation=True))
        else:
            mc.warning(f"Guide '{guide}' does not exist.")
            return None

    # Calculate average position
    center_x = sum(p[0] for p in positions) / len(positions)
    center_y = sum(p[1] for p in positions) / len(positions)
    center_z = sum(p[2] for p in positions) / len(positions)

    return [center_x, center_y, center_z]

def get_guide_positions():
    """Gets world-space positions for all eye guides and stores them in a global list."""
    global guide_pos
    guide_names = [
 
        "L_EyeGuideTop",
        "L_EyeGuideBot",
        "L_EyeGuideIn",
        "L_EyeGuideOut",
        "L_EyeGuide_Back",
        "L_EyeGuide_Front"
    ]
    
    # Query the world-space positions
    guide_pos = [mc.xform(guide, query=True, worldSpace=True, translation=True) for guide in guide_names]
    
    return guide_pos

def find_corner_bone_positions():
    """Calculate the intermediate bone positions for a circular shape."""
    global guide_pos  # Assuming guide_pos is already populated

    # Extract positions
    center = guide_pos[0]
    top = guide_pos[1]
    bottom = guide_pos[2]
    left = guide_pos[3]  # 'In'
    right = guide_pos[4]  # 'Out'

    # Calculate radii
    radius_x = abs(right[0] - center[0])  # Horizontal radius
    radius_y = abs(top[1] - center[1])    # Vertical radius

    # Corner bone positions using 45-degree angles
    corners = []
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)  # Convert degrees to radians
        x = center[0] + radius_x * math.cos(rad)
        y = center[1] + radius_y * math.sin(rad)
        z = center[2]  # Assuming it's aligned with the main guides

        corners.append([x, y, z])

    return corners  # Returns a list of 4 corner positions








def build_L_EyeGeo():
    """Creates a smooth box using guide distances, rotates it, and moves it to the center."""
    vertical_data = calc_vertical_eye("L_EyeGuideTop", "L_EyeGuideBot")
    horizontal_data = calc_horizontal_eye("L_EyeGuideIn", "L_EyeGuideOut")
    thickness = calc_guide_thickness("L_EyeGuide_Back", "L_EyeGuide_Front")
    center = calc_guide_center()

    if not vertical_data or not horizontal_data or thickness is None or center is None:
        mc.warning("Could not retrieve necessary measurements. Box creation aborted.")
        return

    vertical_dist, _, _, _, vertical_angle = vertical_data
    horizontal_dist, _, _, _, horizontal_angle = horizontal_data

    #if mc.objExists("L_EyeGeo"):self.create_curve(name=self.ctrl_name, shape=self.shape, axis=self.axis, scale=self.ctrl_scale):
    #    mc.delete("L_EyeGeo")

    cube = mc.polyCube(name="L_EyeGeo", width=horizontal_dist, height=vertical_dist, depth=thickness)[0]

    # Move to center
    mc.xform(cube, worldSpace=True, translation=center)

    # Rotate based on adjusted angles
    mc.rotate(vertical_angle, horizontal_angle, 0, cube, absolute=True)

    # Smooth the cube with 3 divisions
    mc.polySmooth(cube, divisions=3)

    # Scale the cube by 1.15 in all axes
    mc.scale(1.15, 1.15, 1.15, cube)

    # Delete history and freeze transforms
    mc.delete(cube, ch=True)  # Delete history
    mc.makeIdentity(cube, apply=True, rotate=True, scale=True, translate=True)  # Freeze transforms
    mc.select(clear=True)

    print(f"Created 'L_EyeGeo' at {center} with dimensions: W={horizontal_dist}, H={vertical_dist}, D={thickness}")
    print(f"Rotated 'L_EyeGeo' by Vertical Angle: {vertical_angle}°, Horizontal Angle: {horizontal_angle}°")
    print("Applied smoothing with 3 divisions.")
    print("Scaled 'L_EyeGeo' by 1.15 in all axes.")
    print("Deleted history and frozen transforms on 'L_EyeGeo'.")






def build_L_skeleton():
    vertical_data = calc_vertical_eye("L_EyeGuideTop", "L_EyeGuideBot")
    horizontal_data = calc_horizontal_eye("L_EyeGuideIn", "L_EyeGuideOut")
    thickness = calc_guide_thickness("L_EyeGuide_Back", "L_EyeGuide_Front")
    vertical_dist, _, _, _, vertical_angle = vertical_data
    horizontal_dist, _, _, _, horizontal_angle = horizontal_data

    center = calc_guide_center()

    if center is None:
        mc.warning("Center position could not be found. Skeleton creation aborted.")
        return

    # Create center joint
    center_joint = mc.joint(name="L_Eye_Center_jnt")
    mc.xform(center_joint, worldSpace=True, translation=center)
    mc.joint(center_joint, edit=True, radius=0.2, zso=True, oj="xyz", secondaryAxisOrient="yup")

    # Create joints for Top, Bottom, In, and Out guides
    guides = {
        "Top": "L_EyeGuideTop",
        "Bot": "L_EyeGuideBot",
        "In": "L_EyeGuideIn",
        "Out": "L_EyeGuideOut"
    }

    cardinal_orientations = {
        "Top": 0,
        "In": 90,
        "Bot": 180,
        "Out": 270
    }

    joints = {}

    for guide_name, guide_obj in guides.items():
        if mc.objExists(guide_obj):
            guide_pos = mc.xform(guide_obj, query=True, worldSpace=True, translation=True)
            joint = mc.joint(name=f"L_Eye_{guide_name}_jnt")
            mc.xform(joint, worldSpace=True, translation=guide_pos)
            mc.joint(joint, edit=True, radius=0.2, zso=True, oj="xyz", secondaryAxisOrient="yup")
            mc.joint(joint, edit=True, orientation=[vertical_angle, horizontal_angle, cardinal_orientations[guide_name]])
            mc.parent(joint, center_joint)  # Parent it so it follows the center orientation
            joints[guide_name] = joint
        else:
            mc.warning(f"Guide '{guide_name}' does not exist. Skipping {guide_name} joint.")

    # Calculate semi-axes for the ellipse
    a = horizontal_dist / 2  # Semi-major axis
    b = vertical_dist / 2    # Semi-minor axis

    # Create Corner Joints (at 45-degree angles)
    corner_names = ["TopRight", "TopLeft", "BotLeft", "BotRight"]
    corner_positions = []
    corner_joints = []
    corner_orientations = {
        "TopRight": 315,
        "TopLeft": 45,
        "BotLeft": 135,
        "BotRight": 225
    }

    for i, angle in enumerate([45, 135, 225, 315]):  # Angles for corners
        rad = math.radians(angle)
        corner_x = center[0] + (a * math.cos(rad))
        corner_y = center[1] + (b * math.sin(rad))
        corner_z = center[2]  # Assuming eye lies flat on XY plane

        # Create joint at calculated position
        corner_joint = mc.joint(name=f"L_Eye_{corner_names[i]}_jnt")
        mc.xform(corner_joint, worldSpace=True, translation=[corner_x, corner_y, corner_z])
        mc.joint(corner_joint, edit=True, radius=0.2)
        mc.parent(corner_joint, center_joint)  # Parent it under center joint

        # Reorient joint to face the center joint with cardinal orientation
        mc.joint(corner_joint, edit=True, zso=True, oj="xyz", secondaryAxisOrient="yup")
        mc.joint(corner_joint, edit=True, orientation=[vertical_angle, horizontal_angle, corner_orientations[corner_names[i]]])

        corner_positions.append([corner_x, corner_y, corner_z])
        corner_joints.append(corner_joint)

    print("Skeleton Created with Correctly Oriented Joints.")










def bind_skin():
    """Binds skin to the eye geo using the selected bones."""
    # List of bone names
    bones = [
        "L_Eye_Center_jnt",
        "L_Eye_Top_jnt",
        "L_Eye_Bot_jnt",
        "L_Eye_In_jnt",
        "L_Eye_Out_jnt",
        "L_Eye_TopRight_jnt", 
        "L_Eye_TopLeft_jnt", 
        "L_Eye_BotLeft_jnt", 
        "L_Eye_BotRight_jnt"
    ]

    # Eye geometry name
    eye_geo = "L_EyeGeo"  # Change this if your eye geo has a different name

    # Check if all bones and geometry exist in the scene
    for bone in bones:
        if not mc.objExists(bone):
            mc.warning(f"Bone '{bone}' does not exist in the scene. Skin binding aborted.")
            return

    if not mc.objExists(eye_geo):
        mc.warning(f"Eye geometry '{eye_geo}' does not exist in the scene. Skin binding aborted.")
        return

    # Select bones and geometry
    mc.select(bones + [eye_geo])

    # Bind the skin
    mc.skinCluster(toSelectedBones=True, name="L_Eye_SkinCluster")

    print("Skin binding complete.")

    try:
        import ngSkinTools2; ngSkinTools2.workspace_control_main_window(); ngSkinTools2.open_ui()
    except Exception as e:
        print(e)

    rWeightNgIO.read_skin('L_EyeGeo', f'{groups}/bobo/character/Rigs/DotEye', 'Eye_Weights')
    #try:
     #   ngst_api.import_json('L_EyeGeo', '/groups/bobo/character/Rigs/DotEye/Eye_Weights.json', vertex_transfer_mode="vertexId")
    #except:
     #   mc.error('Skin weights file {} does not exist.')
    #ngst_api.import_json('L_EyeGeo', '/groups/bobo/character/Rigs/DotEye/Eye_Weights.json', vertex_transfer_mode="vertexId")






def build_controls():

    vertical_data = calc_vertical_eye("L_EyeGuideTop", "L_EyeGuideBot")
    horizontal_data = calc_horizontal_eye("L_EyeGuideIn", "L_EyeGuideOut")
    thickness = calc_guide_thickness("L_EyeGuide_Back", "L_EyeGuide_Front")
    vertical_dist, _, _, _, vertical_angle = vertical_data
    horizontal_dist, _, _, _, horizontal_angle = horizontal_data
    cardinal = 0
    center = calc_guide_center()

    #Master Control
    ctrl_grp = mc.group(em=True, name="DotEye_control_grp")
    rCtrl.Control(parent=ctrl_grp, shape='Arrows', side='L', suffix='CTRL', name='Master', axis='z', group_type='main', rig_type='primary', translate=center, rotate=(vertical_angle, 90, 0), ctrl_scale=.3)
    master_ctrl = 'Master_L_CTRL'

    """Builds controls for each eye joint."""
    cntr_under = []
    for jnt in ["L_Eye_Top_jnt", "L_Eye_Bot_jnt", "L_Eye_In_jnt", "L_Eye_Out_jnt", "L_Eye_TopRight_jnt", "L_Eye_TopLeft_jnt", "L_Eye_BotLeft_jnt", "L_Eye_BotRight_jnt"]:
        if not mc.objExists(jnt):
            mc.warning(f"Joint {jnt} does not exist in the scene.")
            continue  # Skip to the next joint if this one is missing

        cardinal = 0
        if jnt == "L_Eye_Top_jnt":
            cardinal = 90 -90
        elif jnt == "L_Eye_Out_jnt":
            cardinal = 180 -90
        elif jnt == "L_Eye_Bot_jnt":
            cardinal = 270 -90
        elif jnt == "L_Eye_In_jnt":
            cardinal = 0 -90
        elif jnt == "L_Eye_TopRight_jnt":
            cardinal = 315
        elif jnt == "L_Eye_TopLeft_jnt": 
            cardinal = 45
        elif jnt == "L_Eye_BotLeft_jnt": 
            cardinal = 135
        elif jnt == "L_Eye_BotRight_jnt": 
            cardinal = 225
        else:
            pass
        # Get joint position
        pos = mc.xform(jnt, query=True, worldSpace=True, translation=True)
        

        #create control
        ctrl_name = jnt.replace("_jnt", "")
        sub_ctrl = rCtrl.Control(parent=master_ctrl, shape='circle', side='L', suffix='CTRL', name=ctrl_name, axis='x', group_type='main', rig_type='primary', translate=pos, rotate=(vertical_angle, horizontal_angle, cardinal), ctrl_scale=.3)
        cntr_under.append(f'{ctrl_name}_L_CTRL_CNST_GRP')


def buildshapes():
    #try:
    #mc.blendShape(n='breath_blendshapes', foc=True, ip=groups + f'/dungeons/character/Rigging/Rigs/{character}/Skin/breath_shapes.shp')
    blend_node = mc.blendShape("L_EyeGeo", n='L_DotEyeShape', ip=f'{groups}/bobo/character/Rigs/DotEye/DotEyeShapes.shp')[0]
    #except:
        #print('No Shapes')

def parentcontrols():
    for jnt in ["L_Eye_Top_jnt", "L_Eye_Bot_jnt", "L_Eye_In_jnt", "L_Eye_Out_jnt", "L_Eye_TopRight_jnt", "L_Eye_TopLeft_jnt", "L_Eye_BotLeft_jnt", "L_Eye_BotRight_jnt"]:
        if not mc.objExists(jnt):
            mc.warning(f"Joint {jnt} does not exist in the scene.")
            continue  # Skip to the next joint if this one is missing
        
        ctrl_name = jnt.replace("_jnt", "_L_CTRL")
        mc.parentConstraint(ctrl_name, jnt, mo=True)
    mc.parentConstraint('Master_L_CTRL', 'L_Eye_Center_jnt', mo=True)
    #Talk to kaylee about the constrain situation 
    #mc.geometryConstraint(character, 'Master_L_CTRL')
    #mc.aimConstraint('L_Aim_Guide', 'Master_L_CTRL', aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="scene", mo=True)


def influence():
    #and infleunce options on the top and bottom controls for their corner controls
    pass


def uvswitch()
    #add a uv switch for shocked eyes and anime eyes
    pass


def parentalcontrols():
    #Set Limits
    pass   


def attr():
    #set custom on master
    for attr in ['square', 'star', 'cresent']:
        mc.addAttr('Master_L_CTRL', longName=attr, attributeType='float', keyable=True, min=0, max=10)
        #mc.connectAttr(f'Master_L_CTRL.{attr}', f'L_DotEyeShape.{attr}')
        remap_node = mc.createNode("remapValue", name=f"{attr}_remap")
        mc.connectAttr(f"Master_L_CTRL.{attr}", f"{remap_node}.inputValue", force=True)
        mc.setAttr(f"{remap_node}.inputMin", 0)  # Min input value
        mc.setAttr(f"{remap_node}.inputMax", 10)  # Max input value
        mc.setAttr(f"{remap_node}.outputMin", 0)  # Min output value
        mc.setAttr(f"{remap_node}.outputMax", 1)  # Max output value
        mc.connectAttr(f"{remap_node}.outValue", f"L_DotEyeShape.{attr}", force=True)

    for jnt in ['Top', 'Bot']:
        #'L_Eye_Top_L_CTRL'
        remap_node = mc.createNode("remapValue", name=f"{jnt}_remap")
        mc.connectAttr(f"L_Eye_{jnt}_L_CTRL.tx", f"{remap_node}.inputValue", force=True)
        mc.setAttr(f"{remap_node}.inputMin", 0)  # Min input value
        mc.setAttr(f"{remap_node}.inputMax", -1)  # Max input value
        mc.setAttr(f"{remap_node}.outputMin", 0)  # Min output value
        mc.setAttr(f"{remap_node}.outputMax", 1)  # Max output value
        mc.connectAttr(f"{remap_node}.outValue", f"L_DotEyeShape.{jnt}_in", force=True)

        remap_node = mc.createNode("remapValue", name=f"{jnt}_remap2")
        mc.connectAttr(f"L_Eye_{jnt}_L_CTRL.tx", f"{remap_node}.inputValue", force=True)
        mc.setAttr(f"{remap_node}.inputMin", 0)  # Min input value
        mc.setAttr(f"{remap_node}.inputMax", 1)  # Max input value
        mc.setAttr(f"{remap_node}.outputMin", 0)  # Min output value
        mc.setAttr(f"{remap_node}.outputMax", 1)  # Max output value
        mc.connectAttr(f"{remap_node}.outValue", f"L_DotEyeShape.{jnt}_out", force=True)


        #mc.connectAttr(f"L_Eye_{jnt}_L_CTRL.tx", f"L_DotEyeShape.{jnt}_out", force=True)
    
    for jnt in ['In', 'Out']:
        #'L_Eye_Top_L_CTRL'
        remap_node = mc.createNode("remapValue", name=f"{jnt}_remap")
        mc.connectAttr(f"L_Eye_{jnt}_L_CTRL.tx", f"{remap_node}.inputValue", force=True)
        mc.setAttr(f"{remap_node}.inputMin", 0)  # Min input value
        mc.setAttr(f"{remap_node}.inputMax", .5)  # Max input value
        mc.setAttr(f"{remap_node}.outputMin", 0)  # Min output value
        mc.setAttr(f"{remap_node}.outputMax", 1)  # Max output value
        mc.connectAttr(f"{remap_node}.outValue", f"L_DotEyeShape.{jnt}_in", force=True)

        remap_node = mc.createNode("remapValue", name=f"{jnt}_remap2")
        mc.connectAttr(f"L_Eye_{jnt}_L_CTRL.tx", f"{remap_node}.inputValue", force=True)
        mc.setAttr(f"{remap_node}.inputMin", 0)  # Min input value
        mc.setAttr(f"{remap_node}.inputMax", -1)  # Max input value
        mc.setAttr(f"{remap_node}.outputMin", 0)  # Min output value
        mc.setAttr(f"{remap_node}.outputMax", 1)  # Max output value
        mc.connectAttr(f"{remap_node}.outValue", f"L_DotEyeShape.{jnt}_out", force=True)
    









# Run the function

#CleanTest()
get_guide_positions()
build_L_EyeGeo()
build_L_skeleton()
bind_skin()
build_controls()
buildshapes()
parentcontrols()
influence():
parentalcontrols()
attr()