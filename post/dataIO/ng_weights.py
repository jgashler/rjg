import os
import maya.cmds as mc

from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode

def write_skin(mesh, directory, name='skin_weights', force=False):
    path = '{}/{}.json'.format(directory, name)
    if force or not os.path.isfile(path):
        ngst_api.export_json(mesh, file=path)
    else:
        mc.error('The skin weights you are trying to save already exist in the specified directory at {}. Please choose a different directory or set the force flag to True.'.format(path))


def read_skin(mesh, directory, name='skin_weights'):
    path = '{}/{}.json'.format(directory, name)
    if os.path.isfile(path):
        ngst_api.import_json(mesh, file=path, vertex_transfer_mode=VertexTransferMode.vertexId)
    else:
        mc.error('Skin weights file {} does not exist.'.format(path))