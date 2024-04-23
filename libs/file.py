import maya.cmds as mc

# imports a scene, finds all root nodes (no parent) and returns them
def import_hierarchy(path, namespace='default', parent=None):
    if not path:
        return
    mc.file(path, i=True, namespace=namespace)
    root_list = mc.ls(namespace + ':|*')                # this gets all the root nodes
    root_nodes = []
    for root in root_list:
        root_nodes.append(root.split(':')[-1])          # this removes namespace info from the name
    mc.namespace(moveNamespace=(namespace, ':'), force=True)
    mc.namespace(removeNamespace=namespace)
    if parent:
        mc.parent(root_nodes, parent)

    return root_nodes