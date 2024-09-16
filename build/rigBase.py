import maya.cmds as mc
from importlib import reload

import rjg.libs.file as rFile
reload(rFile)

'''
Base class for rigModule. Creates base hierarchy for rig and loads in the model and guides.
'''
class RigBase():
    def __init__(self, model_path=None, guide_path=None):
        self.model_path = model_path
        self.guide_path = guide_path

    def create_module(self):
        self.rig_hierarchy()
        if self.model_path:
            self.load_model()
        if self.guide_path:
            self.load_guide()

    # create base hierarachy
    def rig_hierarchy(self):
        self.root = self.rig_group(name='ROOT')                         # contains all other hierarchy groups
        self.model = self.rig_group(name='MODEL', parent=self.root)     # contains all geometry of a character
        self.rig = self.rig_group(name='RIG', parent=self.root)         # contains all rig systems
        self.skel = self.rig_group(name='SKEL', parent=self.root)       # contains the skeleton driven by the rig

    # imports model into scene and places in hierarchy
    def load_model(self):
        root_nodes = rFile.import_hierarchy(self.model_path)
        mc.parent(root_nodes, self.model)

    # imports guides into the scene
    def load_guide(self):
        self.guide_roots = rFile.import_hierarchy(self.guide_path)
        # should this be the child something? currently I delete the guides at the end of the build script. maybe keep around in a GUIDE group?

    # only creates hierarchy group if it does not exists, returns name of group
    def rig_group(self, empty=True, name=None, **kwargs):
        if not mc.objExists(name):
            grp = mc.group(empty=empty, name=name, **kwargs)
        else:
            grp = name
        return grp