import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
reload(rProp)
reload(rBuild)
reload(rFinal)

mp = 'C:/Users/jgash/Documents/maya/projects/F23/ninja_model.mb'
gp = 'C:/Users/jgash/Documents/maya/projects/F23/ninja_guides.mb'

mc.file(new=True, f=True)

root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

spine = rBuild.build_module(module_type='spine', side='M', part='spine', guide_list=['Hips', 'Spine', 'Spine1', 'Spine2'], ctrl_scale=1, mid_ctrl=True)

mc.delete('Ch24')
mc.delete('Hips')
