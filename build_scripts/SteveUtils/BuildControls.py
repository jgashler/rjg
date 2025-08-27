import rjg.post.dataIO.controls as rCtrlIO
import rjg.libs.control.draw as draw

#rCtrlIO.write_ctrls("G:/bobo/character/Rigs/Bobo/Controls", force=True, name='bobo_control_curves')

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
all_checkbox = None



def export_character(*args):
    selected_char = mc.optionMenu(char_menu, query=True, value=True)
    obj_name = f"{selected_char}_UBM"

    # Check if the object exists in the scene
    if mc.objExists(obj_name):
        rCtrlIO.write_ctrls(f"{groups}/bobo/character/Rigs/{selected_char}/Controls", force=True, name=f'{selected_char}_control_curves')
    else:
        print(f"Warning: Object '{obj_name}' not found in the scene.")

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
    export_window = mc.window("exportWindow", title="Control Exporter", widthHeight=(300, 200), sizeable=True)

    # Create a main layout
    mc.columnLayout(adjustableColumn=True)

    # Character selection dropdown
    mc.text(label="Select Character:")
    char_menu = mc.optionMenu()
    for character in ["Bobo", "Gretchen", "Luciana", "Domingo", "Susaka", "Drummer"]:
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
