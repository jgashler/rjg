import os
import maya.cmds as mc

from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode

def write_skin(mesh, directory, name='skin_weights', force=False):
    file_name = '/groups/dungeons/character/Rigging/Rigs/Rayden/Skin/ng_test.json'
    ngst_api.export_json("RaydenNewTopo2", file=file_name)

    path = '{}/{}.json'.format(directory, name)
    if force or not os.path.isfile(path):
        ngst_api.export_json(mesh, file=path)
    else:
        mc.error('The skin weights you are trying to save already exist in the specified directory at {}. Please choose a different directory or set the force flag to True.'.format(path))


def read_skin(mesh, directory, name='skin_weights'):
    config = InfluenceMappingConfig()
    config.use_distance_matching = True
    config.use_name_matching = False

    path = '{}/{}.json'.format(directory, name)
    if os.path.isfile(path):
        ngst_api.import_json(mesh, file=path, vertex_transfer_mode=VertexTransferMode.vertexId, influences_mapping_config=config)
    else:
        mc.error('Skin weights file {} does not exist.'.format(path))