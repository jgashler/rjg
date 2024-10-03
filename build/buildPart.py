import maya.cmds as mc
from importlib import reload

import rjg.libs.attribute as rAttr
import rjg.build.parts.root as rRoot
import rjg.build.parts.hip as rHip
import rjg.build.parts.chest as rChest
import rjg.build.parts.finger as rFinger
import rjg.build.parts.bipedLimb as rBipedLimb
import rjg.build.parts.clavicle as rClavicle
import rjg.build.parts.hand as rHand
import rjg.build.parts.foot as rFoot
import rjg.build.parts.spine as rSpine
import rjg.build.parts.neck as rNeck
import rjg.build.parts.head as rHead
import rjg.build.parts.metaFinger as rMetaFinger
import rjg.build.parts.fingerAttr as rFingerAttr
import rjg.build.parts.tail as rTail
import rjg.build.parts.floatBone as rFloatBone
import rjg.build.parts.hinge as rHinge
import rjg.build.parts.arbit as rArbit
import rjg.build.parts.lookEyes as rLookEyes
reload(rAttr)
reload(rRoot)
reload(rHip)
reload(rChest)
reload(rFinger)
reload(rBipedLimb)
reload(rClavicle)
reload(rHand)
reload(rFoot)
reload(rSpine)
reload(rNeck)
reload(rHead)
reload(rMetaFinger)
reload(rFingerAttr)
reload(rTail)
reload(rFloatBone)
reload(rHinge)
reload(rArbit)
reload(rLookEyes)

'''
Wrapper for all part modules
'''

MODULE_DICT = {
               'root' : rRoot.Root,
               'hip' : rHip.Hip, 
               'chest' : rChest.Chest, 
               'finger' : rFinger.Finger,
               'biped_limb' : rBipedLimb.BipedLimb,
               'clavicle' : rClavicle.Clavicle,
               'hand' : rHand.Hand,
               'foot' : rFoot.Foot,
               'spine' : rSpine.Spine,
               'neck' : rNeck.Neck,
               'head' : rHead.Head,
               'meta_finger': rMetaFinger.MetaFinger,
               'finger_attr': rFingerAttr.FingerAttr,
               'tail': rTail.Tail,
               'float_bone' : rFloatBone.FloatBone,
               'hinge' : rHinge.Hinge,
               'arbitrary' : rArbit.Arbitrary,
               'look_eyes' : rLookEyes.LookEyes,
               }


def build_module(module_type, **kwargs):
    # creates object from module_type class (kwargs carrying any info specific to that class)
    module = MODULE_DICT[module_type](**kwargs)

    # tags to part group with the module type
    rAttr.Attribute(node=module.part_grp, type='string', name='moduleType', value=module_type, lock=True)

    # refresh to update the viewport after each part is built (turning this off can make the build a little faster, build a toggle somewhere in a UI probably)
    mc.refresh()

    return module