import maya.cmds as mc
import maya.mel as mel
import sys, platform
from importlib import reload

groups = 'G:' if platform.system() == 'Windows' else '/groups'



def export_character(*args):
    """Handles exporting based on selected character and options."""
    selected_char = mc.optionMenu(char_menu, query=True, value=True)
       # Construct the object name
    obj_name = f"{selected_char}_UBM"

    #Build Face Structure

    if not mc.objExists("FACE"):
        mc.group(empty=True, name="FACE")
    
    # Create sub-groups
    sub_groups = ["F_MODEL", "F_RIG", "F_SKEL"]
    for group in sub_groups:
        if not mc.objExists(group):
            mc.group(empty=True, name=group, parent="FACE")
    
    # Create the faceRoot_JNT under F_SKEL
    if not mc.objExists("faceRoot_JNT"):
        face_root_jnt = mc.joint(name="faceRoot_JNT")
        mc.move(0, 0, 0, face_root_jnt)  # Move to origin
        mc.parent(face_root_jnt, "F_SKEL")
    
    # Create the face_M group under F_RIG
    if not mc.objExists("face_M"):
        mc.group(empty=True, name="face_M", parent="F_RIG")


    
    obj_name = f"{selected_char}_UBM"
    # Check if the object exists in the scene
    if mc.objExists(obj_name):
        mc.select(obj_name)
        sel = mc.ls(selection=True)
        print(f"Selected object: {obj_name}")
        UBMGeo = mc.duplicate(sel[0])[0]  # Duplicate the first selected object
        UBMGeo = mc.rename(UBMGeo, "FaceAtOrigin")
        mc.parent(UBMGeo, "F_MODEL")
    else:
        print(f"Warning: Object '{obj_name}' not found in the scene.")

    extras_name = f"{selected_char}_EXTRAS"
    # Check if the object exists in the scene
    if mc.objExists(extras_name):
        mc.select(extras_name)
        sel = mc.ls(selection=True)
        print(f"Selected object: {extras_name}")
        ExtraGRP = mc.duplicate(sel[0])[0]  # Duplicate the first selected object
        ExtraGRP = mc.rename(ExtraGRP, "F_EXTRAS")
        mc.parent(ExtraGRP, "F_MODEL")
    else:
        print(f"Warning: Object '{obj_name}' not found in the scene.")

    try:
        # Check if 'Head' exists
        if not mc.objExists("Head"):
            raise ValueError("Head object not found in the scene!")

        # Duplicate 'Head' without children
        head_dup = mc.duplicate("Head", name="head_root", parentOnly=True)[0]

        # Check if 'faceRoot_JNT' exists
        if not mc.objExists("faceRoot_JNT"):
            raise ValueError("faceRoot_JNT does not exist! Please run the group creation script first.")

        # Parent 'head_root' under 'faceRoot_JNT'
        mc.parent(head_dup, "faceRoot_JNT")

    except Exception as e:
        mc.warning(f"Error: {e}")

    mc.select("FACE")
    mc.file(f"{groups}/Bobo/character/Rigs/{selected_char}_Face/{selected_char}Face_Prep.mb", force=True, options="v=0;", type="mayaBinary", exportSelected=True)
    mc.delete("FACE")



def cancel_export(*args):
    """Closes the export window."""
    global export_window
    if mc.window(export_window, exists=True):
        mc.deleteUI(export_window, window=True)

def create_export_window():
    """Creates the character export UI window."""
    global export_window, char_menu, model_checkbox, guides_checkbox, extras_checkbox

    # Close existing window if it exists
    if mc.window("exportWindow", exists=True):
        mc.deleteUI("exportWindow", window=True)

    # Create window
    export_window = mc.window("exportWindow", title="Character Exporter", widthHeight=(300, 200), sizeable=True)

    # Create a main layout
    mc.columnLayout(adjustableColumn=True)

    # Character selection dropdown
    mc.text(label="Select Character:")
    char_menu = mc.optionMenu()
    for character in ["Bobo", "Gretchen"]:
        mc.menuItem(label=character)

    # Buttons
    mc.separator(height=10, style='none')
    mc.rowLayout(numberOfColumns=2, columnAlign=(1, 'center'), columnWidth2=(140, 140))
    mc.button(label="Export", command=export_character)
    mc.button(label="Cancel", command=cancel_export)

    # Show window
    mc.showWindow(export_window)

# Create the UI window
create_export_window()
