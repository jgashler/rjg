import maya.cmds as mc

def create_pxWrap(*argv):
    a = argv if len(argv) > 1 else argv[0]

    driven = a[:-1]
    driver = a[-1]

    #print(f"adding driver: {driver} to driven: {driven}")
    mc.select(driven)
    pxWrap = mc.proximityWrap()
    mc.proximityWrap(pxWrap, e=True, addDrivers=driver)
    mc.setAttr(pxWrap[0] + '.falloffScale', 15.0)