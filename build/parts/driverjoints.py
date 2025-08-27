import maya.cmds as mc

def create_driver_joints(default_mult=10.0, ctrl_suffix="_CTRL", joint_suffix="_Driver", controls=[], parent=None):
    selected_controls = controls

    if not selected_controls:
        mc.warning("No controls selected.")
        return

    driver_joint_list = []
    for ctrl in selected_controls:
        # Add DriverMult attribute
        if not mc.attributeQuery("DriverMult", node=ctrl, exists=True):
            mc.addAttr(ctrl, longName="DriverMult", attributeType="double", defaultValue=default_mult, keyable=True)

        # Get position of control
        pos = mc.xform(ctrl, query=True, worldSpace=True, translation=True)

        # Create joint at world position, don't inherit rotation
        base_name = ctrl.replace(ctrl_suffix, "")
        joint_name = base_name + joint_suffix

        mc.select(clear=True)
        driver_joint = mc.joint(name=joint_name, position=pos)
        mc.setAttr(driver_joint + ".rotate", 0, 0, 0)
        mc.setAttr(driver_joint + ".radius", 0.1)
        mc.makeIdentity(driver_joint, apply=True, t=1, r=1, s=1, n=0)

        # Create multiplyDivide node
        mult_node = mc.createNode("multiplyDivide", name=f"{base_name}_DriverMult_node")

        # Connect control translate to multiplyDivide input1
        mc.connectAttr(ctrl + ".translateX", mult_node + ".input1X", force=True)
        mc.connectAttr(ctrl + ".translateY", mult_node + ".input1Y", force=True)
        mc.connectAttr(ctrl + ".translateZ", mult_node + ".input1Z", force=True)

        # Connect DriverMult to input2 (all axes)
        mc.connectAttr(ctrl + ".DriverMult", mult_node + ".input2X", force=True)
        mc.connectAttr(ctrl + ".DriverMult", mult_node + ".input2Y", force=True)
        mc.connectAttr(ctrl + ".DriverMult", mult_node + ".input2Z", force=True)

        # Connect output of mult to joint rotation
        mc.connectAttr(mult_node + ".outputX", driver_joint + ".rotateX", force=True)
        mc.connectAttr(mult_node + ".outputY", driver_joint + ".rotateY", force=True)
        mc.connectAttr(mult_node + ".outputZ", driver_joint + ".rotateZ", force=True)

        if parent != None:
            mc.parent(driver_joint, parent)
        driver_joint_list.append(driver_joint)
    
    return driver_joint_list

    

    print("✅ Driver joints created successfully.")