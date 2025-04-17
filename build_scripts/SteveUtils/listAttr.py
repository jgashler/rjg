import maya.cmds as mc

def list_attributes(obj_name):
    """
    Lists all attributes of the given object in Maya.
    
    :param obj_name: Name of the Maya object.
    :return: List of attributes.
    """
    if not mc.objExists(obj_name):
        print(f"Object '{obj_name}' does not exist.")
        return []

    attributes = mc.listAttr(obj_name)
    if attributes:
        print(f"Attributes of '{obj_name}':")
        for attr in attributes:
            print(attr)
    else:
        print(f"No attributes found for '{obj_name}'.")
    
    return attributes

# Example usage
object_name = "pSphere1"  # Replace with your object name
attributes = list_attributes(object_name)
