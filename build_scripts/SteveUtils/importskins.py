import maya.cmds as mc
import os
import rjg.post.dataIO.ng_weights as rWeightNgIO
import sys
from importlib import reload
reload(rWeightNgIO)

def find_geo_file(path, geo, extensions=("json", "xml", "weightMap")):
    """
    Search for a file with the name {geo}.{extension} inside the given path.
    Supported extensions: json, xml, weightMap (directory).
    Returns a tuple (full_path, extension) if found, else (None, None).
    """
    for ext in extensions:
        file_path = os.path.join(path, f"{geo}.{ext}")
        if ext == "weightMap":
            if os.path.isdir(file_path):  # it's a folder, not a file
                print(f"Found weightMap folder: {file_path}")
                return file_path, ext
        else:
            if os.path.isfile(file_path):
                print(f"Found file: {file_path}")
                return file_path, ext
    print(f"No file found for {geo} with extensions {extensions} in {path}")
    return None, None


def import_weight_map(weight_map_folder, geo):
    """
    Automates Maya's Import Weight Maps tool (.weightMap format).
    """
    if not mc.objExists(geo):
        print(f"Geometry '{geo}' does not exist in the scene.")
        return

    mc.select(geo, r=True)
    mc.optionVar(sv=("importWeightMapDirectory", weight_map_folder))

    try:
        mel.eval('importSkinMap 2 { "1" };')
        print(f"Successfully imported weight map from '{weight_map_folder}' to '{geo}'.")
    except Exception as e:
        print(f"Error importing weight map: {e}")


def import_weights(geo=None, path=None):
    """
    Main import function deciding which loader to use based on file type.
    """

    if not geo or not path:
        print("Must provide both 'geo' and 'path' arguments.")
        return

    if not mc.objExists(geo):
        print(f"Geometry '{geo}' does not exist in the scene.")
        return

    file_path, ext = find_geo_file(path, geo)

    if not file_path:
        print(f"No matching skin weight file found for {geo} in {path}")
        return

    # Normalize folder and filename
    folder = os.path.dirname(file_path).replace('\\', '/')
    filename = os.path.basename(file_path)

    if ext == 'json':
        print(f"Importing .json skin weights for {geo} from {file_path}")
        rWeightNgIO.read_skin(geo, path, geo)

    elif ext == 'xml':
        print(f"Importing .xml skin weights for {geo} from {file_path}")
        skin = mc.ls(mc.listHistory(geo), type='skinCluster')
        if not skin:
            print(f"No skinCluster found on {geo}. Cannot import weights.")
            return

        skin_cluster = skin[0]
        try:
            mc.deformerWeights(
                filename,
                im=True,
                method='index',
                deformer=skin_cluster,
                path=folder
            )
            print(f"Successfully imported weights from {filename} in {folder} to {geo}")
        except Exception as e:
            print(f"Failed to import weights: {e}")

    elif ext == 'weightMap':
        print(f"Importing weightMap folder for {geo} from {file_path}")
        import_weight_map(file_path, geo)

    else:
        print(f"Unknown file extension '{ext}'. Supported: json, xml, weightMap.")


# Example usage:
# import_weights(geo='Eye_L_Eye_L_Upper_curve_ribbon', path=r'G:\bobo\character\Rigs\Susaka\SkinFiles')
