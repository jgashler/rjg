import maya.cmds as mc
import re

def get_selected_list():
    selection_list = []
    selection = mc.ls(selection=True)
    for obj in selection:
        selection_list.append(obj)
    return selection_list



def connect_double():
    geo = 'FaceAtOrigin'
