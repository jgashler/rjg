import maya.cmds as cmds
import random

def select_random_subset(seed=0, percent=50):
    """
    Select a random subset of the current selection in Maya.
    
    Args:
        seed (int): Random seed for repeatable selection.
        percent (float): Percentage of objects to select (0-100).
    """
    # Get current selection
    selection = cmds.ls(selection=True, flatten=True)
    if not selection:
        cmds.warning("Nothing is selected.")
        return

    # Clamp percent between 0 and 100
    percent = max(0.0, min(100.0, percent))
    
    # Calculate number of items to select
    random.seed(seed)
    count = int(len(selection) * (percent / 100.0))
    if count == 0:
        cmds.warning("Percentage too low. No objects selected.")
        cmds.select(clear=True)
        return

    # Randomly sample the selection
    selected_subset = random.sample(selection, count)

    # Reselect the new subset
    cmds.select(clear=True)
    cmds.select(selected_subset)

# Example usage:
select_random_subset(seed=42, percent=30)
