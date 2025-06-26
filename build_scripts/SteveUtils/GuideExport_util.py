import maya.cmds as mc
import maya.mel as mel
import sys, platform
from importlib import reload

groups = 'G:' if platform.system() == 'Windows' else '/groups'
    
"""
    first i need a  UI box that is rescalable and has a exit button
    that will allow me to select a Character in a list 
    CharList = ["Bobo", "Gretchen", "Bee"]
    Then I will need to select what type of export I want (check box style)
            Model
            Guides
            Extras
    at the very bottom of the box i will want a button that says export and one that says cancel
        
"""
# Global variables for UI elements
export_window = None
char_menu = None
model_checkbox = None
guides_checkbox = None
extras_checkbox = None
all_checkbox = None

def export_all(selected_char):
    # Construct the object name
    obj_name = f"{selected_char}_UBM"

    # Check if the object exists in the scene
    if mc.objExists(obj_name):
        mc.file(f"{groups}/bobo/character/Rigs/{selected_char}/{selected_char}_all.mb", force=True, options="v=0;", type="mayaBinary")
    else:
        print(f"Warning: Object '{obj_name}' not found in the scene.")

def export_model(selected_char):
    # Construct the object name
    obj_name = f"{selected_char}_UBM"

    # Check if the object exists in the scene
    if mc.objExists(obj_name):
        mc.select(obj_name)
        print(f"Selected object: {obj_name}")
        mc.file(f"{groups}/bobo/character/Rigs/{selected_char}/{selected_char}_Model.mb", force=True, options="v=0;", type="mayaBinary", exportSelected=True)
    else:
        print(f"Warning: Object '{obj_name}' not found in the scene.")

def export_guides(selected_char):
    # Construct the object name
    obj_name = f"Guides"
    char_check = f"{selected_char}_UBM"
    # Check if the object exists in the scene
    if mc.objExists(char_check):
        if mc.objExists(obj_name):
            mc.select(obj_name)
            print(f"Selected object: {obj_name}")
            mc.file(f"{groups}/bobo/character/Rigs/{selected_char}/{selected_char}_Guides.mb", force=True, options="v=0;", type="mayaBinary", exportSelected=True)
        else:
            print(f"Warning: Object '{obj_name}' not found in the scene.")
    else:
        print(f"Warning: Object '{char_check}' not found in the scene.")

def export_extras(selected_char):
    # Construct the object name
    obj_name = f"{selected_char}_EXTRAS"

    # Check if the object exists in the scene
    if mc.objExists(obj_name):
        mc.select(obj_name)
        print(f"Selected object: {obj_name}")
        mc.file(f"{groups}/bobo/character/Rigs/{selected_char}/{selected_char}_Extras.mb", force=True, options="v=0;", type="mayaBinary", exportSelected=True)
    else:
        print(f"Warning: Object '{obj_name}' not found in the scene.")



def export_character(*args):
    """Handles exporting based on selected character and options."""
    selected_char = mc.optionMenu(char_menu, query=True, value=True)
    selected_model = mc.checkBox(model_checkbox, query=True, value=True)
    selected_guides = mc.checkBox(guides_checkbox, query=True, value=True)
    selected_extras = mc.checkBox(extras_checkbox, query=True, value=True)
    selected_all = mc.checkBox(all_checkbox, query=True, value=True)

    print(f"Exporting character: {selected_char}")
    print(f"Model: {'Yes' if selected_model else 'No'}, Guides: {'Yes' if selected_guides else 'No'}, Extras: {'Yes' if selected_extras else 'No'}")

    # Implement actual export logic here
    if selected_model == True:
        export_model(selected_char)
    else:
        print("Not exporting Model")
    if selected_guides == True:
        export_guides(selected_char)
    else:
        print("Not exporting Guides")
    if selected_extras == True:
        export_extras(selected_char)
    else:
        print("Not exporting Extras")
    if selected_all == True:
        export_all(selected_char)
    else:
        print("Not exporting Extras")

def cancel_export(*args):
    """Closes the export window."""
    global export_window
    if mc.window(export_window, exists=True):
        mc.deleteUI(export_window, window=True)

def create_export_window():
    """Creates the character export UI window."""
    global export_window, char_menu, model_checkbox, guides_checkbox, extras_checkbox, all_checkbox

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
    for character in ["Bobo", "Gretchen", "BoboQuad", "Susaka"]:
        mc.menuItem(label=character)

    # Export type checkboxes
    mc.text(label="Select Export Types:")
    model_checkbox = mc.checkBox(label="Model", value=True)
    guides_checkbox = mc.checkBox(label="Guides", value=True)
    extras_checkbox = mc.checkBox(label="Extras", value=True)
    all_checkbox = mc.checkBox(label="ALL File", value=True)

    # Buttons
    mc.separator(height=10, style='none')
    mc.rowLayout(numberOfColumns=2, columnAlign=(1, 'center'), columnWidth2=(140, 140))
    mc.button(label="Export", command=export_character)
    mc.button(label="Cancel", command=cancel_export)

    # Show window
    mc.showWindow(export_window)

# Create the UI window
create_export_window()
