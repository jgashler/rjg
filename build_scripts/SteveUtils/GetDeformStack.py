import maya.cmds as mc

def get_deformers(mesh):
    """
    Returns a list of deformers affecting the specified mesh.
    
    :param mesh: The name of the mesh object.
    :return: List of deformers affecting the mesh.
    """
    if not mc.objExists(mesh):
        print(f"Error: Mesh '{mesh}' does not exist.")
        return []

    # Get all nodes in history affecting the mesh
    history = mc.listHistory(mesh, pruneDagObjects=True) or []
    
    # Filter for deformer types
    deformer_types = ["skinCluster", "blendShape", "lattice", "wrap", "cluster"]
    deformers = [node for node in history if mc.nodeType(node) in deformer_types]

    return deformers

# Example usage
mesh_name = "Bobo_UBM"  # Change this to your mesh name
deformers = get_deformers(mesh_name)

print(f"Deformers affecting {mesh_name}: {deformers}")
