import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
import rjg.build.prop as rProp
reload(rProp)
reload(rBuild)
reload(rFinal)

mp = ''
gp = '/users/animation/jgashler/Desktop/tail_test.mb'

mc.file(new=True, f=True)

tail_guides = ['Tail'+str(i+1) for i in range(7)]


root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

tail = rBuild.build_module(module_type='tail', side='M', part='tail', guide_list=tail_guides, ctrl_scale=1)

mc.delete('Tail1')