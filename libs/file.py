import maya.cmds as mc

# TODO: namespace only works if set to mixamorig right now
def import_hierarchy(path, namespace='mixamorig'):
    mc.file(path, i=True, namespace=namespace)
    root_list = mc.ls(namespace + ':|*')
    root_nodes = []
    for root in root_list:
        root_nodes.append(root.split(':')[-1])
    mc.namespace(moveNamespace=(namespace, ':'), force=True)
    mc.namespace(removeNamespace=namespace)
    return root_nodes