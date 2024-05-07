import maya.cmds as mc

def make_cMuscleObject(object=None, fat=0.5):

    cmo = mc.createNode('cMuscleObject', name=object + '_cMuscleObject')

    mc.connectAttr(object + '.worldMatrix[0]', cmo + '.worldMatrixStart')
    mc.connectAttr(object + '.worldMesh[0]', cmo + '.meshIn')
    mc.setAttr(cmo + '.draw', 0)
    
    temp = mc.listRelatives(cmo, parent=True)
    mc.parent(cmo, object, s=True, r=True)
    mc.delete(temp)
    
    mc.setAttr(cmo + '.fat', fat)
    
    return cmo
    
    
def make_cMuscleKeepOut(object=None, in_direction=(0, 1, 0)):
    mc.select(object)
    mc.addAttr(at='float', longName='msgKeepOut', r=False)
    mc.addAttr(at='float', longName='msgKeepOutDriven', r=False)
    mc.addAttr(at='float', longName='msgKeepOutXForm', r=False)
    
    cmkos = mc.createNode('cMuscleKeepOut', name=object + '_cMuscleKeepOutShape1')
    cmko = mc.rename(mc.listRelatives(cmkos, parent=True), object + '_cMuscleKeepOut1')
    cmkod = mc.createNode('transform', name=cmko + 'Driven')
    
    mc.connectAttr(cmko + '.message', object + '.msgKeepOutXForm')
    mc.connectAttr(cmkos + '.message', object + '.msgKeepOut')
    mc.connectAttr(cmkod + '.message', object + '.msgKeepOutDriven')
    
    mc.connectAttr(cmko + '.worldMatrix[0]', cmkos + '.worldMatrixAim')
    mc.connectAttr(cmkos + '.outTranslateLocal', cmkod + '.translate')
    
    mc.parent(object, cmkod)
    mc.parent(cmkod, cmko)
    
    mc.setAttr(cmko + '.inDirectionX', in_direction[0])
    mc.setAttr(cmko + '.inDirectionY', in_direction[1])
    mc.setAttr(cmko + '.inDirectionZ', in_direction[2])
    
    return cmko
    
def connect_muscleToKeepOut(cmko, cmo):
    mc.connectAttr(cmo + '.muscleData', cmko + '.muscleData[0]')
 
cmko = make_cMuscleKeepOut('joint1')    
cmo = make_cMuscleObject('pCube1', fat=0)

connect_muscleToKeepOut(cmko, cmo)



