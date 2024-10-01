import maya.cmds as mc
import rjg.libs.control.ctrl as rCtrl

def create_pxWrap(*argv):
    a = argv if len(argv) > 1 else argv[0]

    driven = a[:-1]
    driver = a[-1]

    #print(f"adding driver: {driver} to driven: {driven}")
    mc.select(driven)
    pxWrap = mc.proximityWrap()
    mc.proximityWrap(pxWrap, e=True, addDrivers=driver)
    mc.setAttr(pxWrap[0] + '.falloffScale', 15.0)


def create_pxPin(x, y, z, target_vtx, n='default', ctrl=False, prop=None):
    pin = mc.spaceLocator(n=n)
    mc.move(x, y, z, r=True, os=True, wd=True)

    mc.select(target_vtx, pin)
    pxPin = mc.ProximityPin()

    if ctrl:
        rig_grp = mc.group(empty=True, n=n + '_M', parent='RIG')
        pin_ctrl = rCtrl.Control(parent=rig_grp, name=n, shape='lollipop', side='M', suffix='CTRL', axis='y', group_type='main', rig_type='primary', translate=pin[0], rotate=(0, 0, 0), ctrl_scale=5)
        pin_ctrl.tag_as_controller()

        #mc.parentConstraint(pin_ctrl.ctrl, pin[0])
        mc.parentConstraint(pin[0], pin_ctrl.top, mo=True)
        mc.parentConstraint(pin_ctrl.ctrl, prop, mo=True)

    mc.delete(pxPin)

    return pin


def reverse_hair_project():
    pass


'''
main_mesh: (str) name of mesh with the blendshape deformer
blandshape: name of the blendshape
driver: control attribute to drive shape
driven: corrective blend shape
driver_range: attribute values for key driver
driven_range: blend shape envelope values for key driven 
index: index to insert
'''
def connect_corrective(main_mesh, blendshape, driver, driven, driver_range, driven_range, curve='linear', index=0):
    mc.select(driven)
    mc.blendShape(blendshape, e=True, target=[main_mesh, index, driven, 1], w=[index, 0])

    org = mc.getAttr(driver)

    bst = blendshape + '.' + driven

    for a, b in zip(driver_range, driven_range):
        mc.setAttr(driver, a)
        mc.setAttr(bst, b)
        mc.select(blendshape)
        mc.setDrivenKeyframe(at=driven, cd=driver, itt=curve, ott=curve)

    mc.setAttr(driver, org)
    mc.select(clear=True)

    mc.delete(driven)


def corrective_setup(mesh, input=None):
    if not mc.objExists('main_blendshapes'):
        mc.select(mesh)
        bs = mc.blendShape(n='main_blendshapes', automatic=True)
        mc.select(clear=True)
    
    imp = mc.file(input[0], i=True)

    for id, s in enumerate(input[1:]):
       connect_corrective(s[0], 'main_blendshapes', s[1], s[2], s[3], s[4], s[5], id+49)

    mc.delete("*_DEFAULT")


def import_poseInterpolator(path):
    try:
        from maya import mel
        mel.eval(f'poseInterpolatorImportPoses "{path}" 1;')
        mc.select('*_poseInterpolator')
        pi = mc.ls(selection=True)
        mc.parent(pi, 'RIG')
    except Exception as e:
        mc.warning(e)