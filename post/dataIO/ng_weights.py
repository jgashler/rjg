import os, json
import maya.cmds as mc
import pipe.util as pu

from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import VertexTransferMode, InfluenceMappingConfig

from importlib import reload

import rjg.post.dataIO.weights as rWeightIO
reload(rWeightIO)

def write_skin(mesh, directory, name='skin_weights', force=False):
    path = '{}/{}.json'.format(directory, name)
    if force or not os.path.isfile(path):
        ngst_api.export_json(mesh, file=path)
    else:
        mc.error('The skin weights you are trying to save already exist in the specified directory at {}. Please choose a different directory or set the force flag to True.'.format(path))


def read_skin(mesh, directory, name='skin_weights'):
    path = '{}/{}.json'.format(directory, name)
    if os.path.isfile(path):
        ngst_api.import_json(mesh, file=path, vertex_transfer_mode="vertexId")
    else:
        mc.error('Skin weights file {} does not exist.'.format(path))
        
def clothing_batch_export(character=None, force=False):
    if not character:
        mc.error('Select the character whose clothes you are trying to export.')
        return
        
    selected = mc.ls(selection=True)
    par_dir_path = pu.get_rigging_path() / "Rigs" / character / "Skin" / "Clothes"
    
    for s in selected:
        # make sure that each selected skinCluster has ngSkinTools data node
        ngst_api.init_layers(s)
        
        # if uninitialized, create base layer
        layers = ngst_api.Layers(s)
        if len(layers.list()) == 0:
            layers.add("Base Weights")
        
        dir_path = par_dir_path / s
        
        if force and not os.path.exists(dir_path):
            print(f"Creating new directory at {dir_path}")
            os.mkdir(dir_path)
            
        if not os.path.exists(dir_path):
            mc.warning(f"Failed to save weights for {s} because no directory exists. Set 'force=True' to enable directory creation.")
            continue
            
        # determine latest existing version and increment
        ls_dir = dir_path.iterdir()
        latest_version = 0
        
        for item in ls_dir:
            version = int(str(item).split(".")[-2])
            if version > latest_version:
                latest_version = version
                
        v_string = str(latest_version + 1).zfill(3)

        # save file to path
        full_name = dir_path / f"{s}.{v_string}.json"
        ngst_api.export_json(s, file=str(full_name))
        
def clothing_batch_export_v2(character, force=False):
    if not character:
        mc.error('Select the character whose clothes you are trying to export.')
        return
        
    selected = mc.ls(selection=True)
    par_dir_path = pu.get_rigging_path() / "Rigs" / character / "Skin" / "Clothes"
    
    for s in selected:
        # make sure that each selected skinCluster has ngSkinTools data node
        ngst_api.init_layers(s)
        
        # if uninitialized, create base layer
        layers = ngst_api.Layers(s)
        if len(layers.list()) == 0:
            layers.add("Base Weights")
        
        dir_path = par_dir_path / s
        
        if force and not os.path.exists(dir_path):
            print(f"Creating new directory at {dir_path}")
            os.mkdir(dir_path)
            
        if not os.path.exists(dir_path):
            mc.warning(f"Failed to save weights for {s} because no directory exists. Set 'force=True' to enable directory creation.")
            continue
            
        # determine latest existing version and increment
        ls_dir = dir_path.iterdir()
        latest_version = 0
        
        for item in ls_dir:
            version = int(str(item).split(".")[-2])
            if version > latest_version:
                latest_version = version
                
        v_string = str(latest_version + 1).zfill(3)

        # save file to path
        full_name = dir_path / f"{s}.{v_string}.json"
        rWeightIO.write_skin(full_name, name=None, force=True, full=True)
        
    

def clothing_batch_import_v2(character):
    par_dir_path = pu.get_rigging_path() / "Rigs" / character / "Skin" / "Clothes"
    
    par_ls_dir = os.listdir(par_dir_path)
    
    for t in par_ls_dir:
        dir_path = par_dir_path / t
        
        target = str(dir_path).split('/')[-1]
        
        ls_dir = dir_path.iterdir()
        latest_version = 0
        
        for item in ls_dir:
            version = int(str(item).split(".")[-2])
            if version > latest_version:
                latest_version = version

        v_string = str(latest_version).zfill(3)
        
        path = par_dir_path / f"{target}.{v_string}.json"
        
        print(str(path))
        
        
        
        
def clothing_batch_import(character):
    par_dir_path = pu.get_rigging_path() / "Rigs" / character / "Skin" / "Clothes"
    
    par_ls_dir = os.listdir(par_dir_path)
    
    for t in par_ls_dir:
        dir_path = par_dir_path / t
        
        target = str(dir_path).split('/')[-1]
        
        ls_dir = dir_path.iterdir()
        latest_version = 0
        
        for item in ls_dir:
            version = int(str(item).split(".")[-2])
            if version > latest_version:
                latest_version = version

        v_string = str(latest_version).zfill(3)
        
        path = par_dir_path / f"{target}.{v_string}.json"
        print(str(path))
        ngst_api.import_json(target, file=str(path), vertex_transfer_mode="vertexId")
        #ngst_api.import_json(target, file=str(path), vertex_transfer_mode=VertexTransferMode.vertexId)
        

        
        
def init_skc(skc):
    layers = ngst_api.init_layers(skc)
    layers = ngst_api.Layers(skc)
    if len(layers.list()) == 0:
        layers.add("Base Weights")
        
        
def ngst2tools_v2(**kwargs):
    
    from ngSkinTools2.api.log import getLogger
    log = getLogger("plugin")
    
    log.debug("ngst2tools [%r]", kwargs)
    result = cmds.ngst2Tools(json.dumps(kwargs))
    if result is not None:
        print(f"result: {result}")
        print(type(result))
        result = json.loads(result)
    return result
        
        
        
     
        
    
    

        
        
    
#clothing_batch_export_v2('Rayden')
#clothing_batch_import_v2('Rayden')