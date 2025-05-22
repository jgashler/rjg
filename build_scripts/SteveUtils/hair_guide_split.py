import maya.cmds as mc
 
def process_shapes():
    selection = mc.ls(sl=True, long=True)  # Get selection with full path names
    if not selection:
        mc.warning('Please select at least one object.')
        return
 
    for obj in selection:
        shapes = mc.listRelatives(obj, children=True, type='shape', fullPath=True) or []
        for shape in shapes:
            newTrans = mc.createNode('transform', name='hairCrv#')
            mc.parent(shape, newTrans, shape=True)
            mc.warning('Processed: {}'.format(shape))
 
def create_ui():
    windowID = 'hairCrvToolWindow'
 
    if mc.window(windowID, exists=True):
        mc.deleteUI(windowID)
 
    mc.window(windowID, title='Hair Curve Tool', sizeable=False, resizeToFitChildren=True)
    mc.columnLayout(adjustableColumn=True)
    mc.button(label='extract Individual Curves', command=lambda x: process_shapes())
    mc.showWindow()
 
create_ui()