import maya.cmds as mc
import json, os

def write_skin(directory, name='skin_weights', force=False):
    skin = build_skin_dict()
    path = '{}/{}.json'.format(directory, name)
    dump = json.dumps(skin, indent=4)

    if force or os.path.isfile(path) == False:
        file = open(path, 'w')
        file.write(dump)
        file.close()
    else:
        mc.error('The skin weights you are trying to save already exist in the specified directory at {}. Please choose a different directory or set the force flag to True.'.format(path))

    for cluster in skin:
        mc.deformerWeights(cluster + '.xml', export=True, path=directory, deformer=cluster)

def read_skin(directory, weights_file='skin_weights.json'):
    path = directory + weights_file
    if os.path.isfile(path):
        file = open(path, 'r')
        skin = json.loads(file.read())
    else:
        mc.error('Skin weights file {} does not exist.'.format(path))

    for cluster, cluster_dict in skin.items():
        inf = cluster_dict['influences'] + [cluster_dict['geometry']]
        max_inf = cluster_dict['max_influences']

        if not mc.objExists(cluster):
            mc.skinCluster(inf, maximumInfluences=max_inf, toSelectedBones=True, name=cluster)
        
        mc.deformerWeights(cluster + '.xml', im=True, deformer=cluster, method='index', path=directory)
        mc.skinCluster(cluster, edit=True, forceNormalizeWeights=True)


def build_skin_dict():
    skin_dict = {}
    for cluster in mc.ls(type='skinCluster'):
        geo = mc.skinCluster(cluster, q=True, geometry=True)[0]
        inf = mc.skinCluster(cluster, q=True, influence=True)
        max_inf = mc.skinCluster(cluster, q=True, maximumInfluences=True)
        skin_dict[cluster] = {'geometry' : geo,
                              'influences' : inf,
                              'max_influences' : max_inf}
    return skin_dict
        
