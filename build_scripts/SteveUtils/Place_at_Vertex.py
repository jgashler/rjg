import maya.cmds as cmds
import maya.api.OpenMaya as om
import math
import random
def instance_asset_on_vertices_with_jitter(asset_name, rotation_jitter=20, scale_jitter=0.2):
    sel = cmds.ls(sl=True, fl=True)
    verts = cmds.filterExpand(sel, sm=31)
    if not verts:
        cmds.error("Please select vertices.")

    mesh_name = verts[0].split('.')[0]
    sel_list = om.MSelectionList()
    sel_list.add(mesh_name)
    dag_path = sel_list.getDagPath(0)
    mesh_fn = om.MFnMesh(dag_path)

    instances = []

    for vtx in verts:
        index = int(vtx.split("[")[-1][:-1])
        pos = mesh_fn.getPoint(index, om.MSpace.kWorld)
        normal = mesh_fn.getVertexNormal(index, True, om.MSpace.kWorld)

        # Build orthonormal basis where Y = normal
        y_axis = om.MVector(normal).normalize()
        arbitrary = om.MVector(1, 0, 0) if abs(y_axis * om.MVector(1, 0, 0)) < 0.99 else om.MVector(0, 0, 1)
        x_axis = (arbitrary ^ y_axis).normalize()
        z_axis = (x_axis ^ y_axis).normalize()

        # Optional: add random twist around Y (normal)
        angle_rad = math.radians(random.uniform(-rotation_jitter, rotation_jitter))
        cos_theta = math.cos(angle_rad)
        sin_theta = math.sin(angle_rad)

        # Rotate X and Z around Y
        x_axis_twisted = (x_axis * cos_theta) + (z_axis * sin_theta)
        z_axis_twisted = (z_axis * cos_theta) - (x_axis * sin_theta)

        # Build twisted matrix
        rot_matrix = om.MMatrix([
            [x_axis_twisted.x, x_axis_twisted.y, x_axis_twisted.z, 0],
            [y_axis.x,          y_axis.y,         y_axis.z,         0],
            [z_axis_twisted.x, z_axis_twisted.y, z_axis_twisted.z, 0],
            [0,                0,                0,                1]
        ])

        transform_matrix = om.MTransformationMatrix(rot_matrix)
        euler_rot = transform_matrix.rotation()
        rot_deg = [math.degrees(euler_rot.x), math.degrees(euler_rot.y), math.degrees(euler_rot.z)]

        # Duplicate and apply transform
        dup = cmds.duplicate(asset_name, rr=True)[0]
        instances.append(dup)

        grp = cmds.group(dup, n=dup + "_grp")
        cmds.xform(grp, ws=True, t=(pos.x, pos.y, pos.z))
        cmds.xform(grp, ws=True, rotation=rot_deg)

        # Random scale factor
        base_scale = 1.0
        jitter = random.uniform(-scale_jitter, scale_jitter)
        scale_val = base_scale + jitter
        cmds.xform(grp, ws=True, scale=(scale_val, scale_val, scale_val))

    return instances

def instance_asset_on_vertices(asset_name):
    sel = cmds.ls(sl=True, fl=True)
    verts = cmds.filterExpand(sel, sm=31)  # vertex components
    if not verts:
        cmds.error("Please select vertices.")

    mesh_name = verts[0].split('.')[0]
    sel_list = om.MSelectionList()
    sel_list.add(mesh_name)
    dag_path = sel_list.getDagPath(0)
    mesh_fn = om.MFnMesh(dag_path)

    instances = []

    for vtx in verts:
        index = int(vtx.split("[")[-1][:-1])
        pos = mesh_fn.getPoint(index, om.MSpace.kWorld)
        normal = mesh_fn.getVertexNormal(index, True, om.MSpace.kWorld)

        # Create orthonormal basis with Y = normal
        y_axis = om.MVector(normal).normalize()

        # Pick a safe arbitrary vector that is not parallel to normal
        arbitrary = om.MVector(1, 0, 0) if abs(y_axis * om.MVector(1, 0, 0)) < 0.99 else om.MVector(0, 0, 1)

        x_axis = (arbitrary ^ y_axis).normalize()  # cross product gives orthogonal X
        z_axis = (x_axis ^ y_axis).normalize()     # cross product gives orthogonal Z

        # Build rotation matrix
        rot_matrix = om.MMatrix([
            [x_axis.x, x_axis.y, x_axis.z, 0],
            [y_axis.x, y_axis.y, y_axis.z, 0],
            [z_axis.x, z_axis.y, z_axis.z, 0],
            [0,        0,        0,        1]
        ])

        # Convert matrix to transform (translation + rotation)
        transform_matrix = om.MTransformationMatrix(rot_matrix)
        euler_rot = transform_matrix.rotation()
        rot_deg = [math.degrees(euler_rot.x), math.degrees(euler_rot.y), math.degrees(euler_rot.z)]

        # Duplicate asset
        dup = cmds.duplicate(asset_name, rr=True)[0]
        instances.append(dup)

        # Group it and move
        grp = cmds.group(dup, n=dup + "_grp")
        cmds.xform(grp, ws=True, t=(pos.x, pos.y, pos.z))
        cmds.xform(grp, ws=True, rotation=rot_deg)

    return instances

# Select some vertices, then run:
#instance_asset_on_vertices("test")
# Select some vertices, then run:
#instance_asset_on_vertices_with_jitter("Screw", rotation_jitter=30, scale_jitter=0.05)

