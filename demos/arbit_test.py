import maya.cmds as mc
from importlib import reload

import rjg.build.buildPart as rBuild
import rjg.post.finalize as rFinal
reload(rBuild)
reload(rFinal)

mp = ''
gp = '/users/animation/jgashler/Desktop/arbit_test.mb'

mc.file(new=True, f=True)

arbit_guides = ['arb'+str(i+1) for i in range(3)]


root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp)
mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)
    
for ag in arbit_guides:
    arb = rBuild.build_module(module_type='arbitrary', side='M', part=ag, guide_list=mc.getAttr(ag + '.translate'), ctrl_scale=1, par_jnt='head_M_JNT', par_ctrl='head_M_01_CTRL')

mc.delete(arbit_guides)