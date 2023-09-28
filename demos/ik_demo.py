import maya.cmds as mc
from importlib import reload

import rjg.build.parts.ik_chain as rIk
reload(rIk)

ik = rIk.IkChain(side='L', part='arm', guide_list=mc.ls(sl=True), ctrl_scale=1.5, sticky=None, solver=None, pv_guide='auto', offset_pv=0, slide_pv=None, 
                 stretchy=True, twisty=True, bendy=True, segments=4, model_path=None, guide_path=None)
