import maya.cmds as mc
from importlib import reload

import rjg.libs.attribute as rAttr
import rjg.build.parts.root as rRoot
import rjg.build.parts.hip as rHip
import rjg.build.parts.chest as rChest
import rjg.build.parts.finger as rFinger
reload(rAttr)
reload(rRoot)
reload(rHip)
reload(rChest)
reload(rFinger)

MODULE_DICT = {'root' : rRoot.Root,
               'hip' : rHip.Hip, 
               'chest' : rChest.Chest, 
               'finger' : rFinger.Finger,}

def build_module(module_type, **kwargs):
    # creates object from module_type class (kwargs carrying any info specific to that class)
    module = MODULE_DICT[module_type](**kwargs)

    rAttr.Attribute(node=module.part_grp, type='string', name='moduleType', value=module_type, lock=True)
    mc.refresh()

    return module