import os
import maya.cmds as mc
import maya.mel as mel
import rjg.post.dataIO.ng_weights as rWeightNgIO
import sys

def find_geo_file(path, geo, extensions=("json", "xml", "weightMap")):
    """
    Search for a file with the name {geo}.{extension} inside the given path.
    Supported extensions: json, xml, weightMap (as file).
    Returns a tuple (full_path, extension) if found, else (None, None).
    """
    for ext in extensions:
        file_path = os.path.join(path, f"{geo}.{ext}")
        print(f"Checking: {file_path}")
        
        if os.path.isfile(file_path):
            print(f"✅ Found file: {file_path}")
            return file_path, ext

    print(f"❌ No file found for {geo} with extensions {extensions} in {path}")
    return None, None

def import_weight_map(weight_map_folder, geo):
    """
    Automates Maya's Import Weight Maps tool (.weightMap format).
    Note: This will likely open the Import UI since importSkinMap command triggers it.
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

def import_weights_from_xml(xml_path, geo):
    """
    Import skin weights from an XML file using Maya's deformerWeights command.
    This method does not open any UI.
    """
    if not mc.objExists(geo):
        print(f"Geometry '{geo}' does not exist.")
        return
    skin = mc.ls(mc.listHistory(geo), type="skinCluster")
    if not skin:
        print(f"No skinCluster found on '{geo}'.")
        return

    try:
        mc.deformerWeights(
            xml_path,
            im=True,                   # import mode
            method="index",            # match by vertex index (fastest)
            deformer=skin[0]
        )
        print(f"Imported XML weights from {xml_path} into {geo}")
    except Exception as e:
        print(f"Import failed: {e}")

def import_weights(geo=None, path=None):
    """
    Main entry point for importing skin weights.
    Supports:
      - .json using rWeightNgIO
      - .xml using deformerWeights
      - .weightMap using Maya's importSkinMap (may open UI)
    """
    if not mc.objExists(geo):
        print(f"Geo '{geo}' does not exist in the scene.")
        return

    file_path, ext = find_geo_file(path, geo)

    if ext == 'json':
        rWeightNgIO.read_skin(geo, path, geo)
    elif ext == 'xml':
        import_weights_from_xml(file_path, geo)
    elif ext == 'weightMap':
        import_weight_map(file_path, geo)
    else:
        print(f"Unknown or unsupported file type for: {geo}")
