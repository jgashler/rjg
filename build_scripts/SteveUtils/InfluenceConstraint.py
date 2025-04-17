import maya.cmds as mc

'''
First find the Driver and Driven as lists 
next we will take the Driver and give it a new attribute that is a scaler float value between 0 and 10



'''


def Influence_constraint(DriverList, DrivenList, AttrName, DefaultValue):
    if len(DriverList) != len(DrivenList):
        mc.warning("DriverList and DrivenList must have the same length!")
        return

    for driver, driven in zip(DriverList, DrivenList):
        if not mc.objExists(driver) or not mc.objExists(driven):
            mc.warning(f"One of the objects '{driver}' or '{driven}' does not exist.")
            continue

        # Add the influence attribute if it doesn't exist
        if not mc.attributeQuery(AttrName, node=driver, exists=True):
            mc.addAttr(driver, longName=AttrName, attributeType="float", min=0, max=10, defaultValue=DefaultValue, keyable=True)

        group_name = f"{driven}{driver}Influence"
        if not mc.objExists(group_name):
            group = mc.group(driven, name=group_name, r=True, )  # Create empty group

        else:
            mc.warning(f"Group '{group_name}' already exists.")
        # Create the Remap Node
        remap_node_name = f"{driver}{driven}Inf_remap"
        if not mc.objExists(remap_node_name):
            remap_node = mc.createNode("remapValue", name=remap_node_name)
            mc.setAttr(f"{remap_node}.inputMax", 10)
            #print(f"Created remapValue node '{remap_node_name}'")

        # Create the multiplyDivide node
        mult_div_node_name = f"{driver}{driven}Inf_MultDiv"
        if not mc.objExists(mult_div_node_name):
            mult_div_node = mc.createNode("multiplyDivide", name=mult_div_node_name)
            #print(f"Created multiplyDivide node '{mult_div_node_name}'")

        # Connect the driven's translate to multiplyDivide input1
        mc.connectAttr(f"{driver}.translate", f"{mult_div_node}.input1")

        # Connect the driver's attribute to remapValue inputValue
        mc.connectAttr(f"{driver}.{AttrName}", f"{remap_node}.inputValue")

        # Connect the remapValue outValue to multiplyDivide input2X, input2Y, input2Z
        mc.connectAttr(f"{remap_node}.outValue", f"{mult_div_node}.input2X")
        mc.connectAttr(f"{remap_node}.outValue", f"{mult_div_node}.input2Y")
        mc.connectAttr(f"{remap_node}.outValue", f"{mult_div_node}.input2Z")

        # Connect multiplyDivide output to the driven's group translate
        mc.connectAttr(f"{mult_div_node}.output", f"{group}.translate")

        print(f"Connected nodes for {driver} and {driven}")

        

AttrName = 'InnerInfluence'
DefaultValue = 5
DriverList = ['Left_Eye_Outer_01_ctrl', 'Left_Eye_Outer_02_ctrl', 'Left_Eye_Outer_03_ctrl', 'Left_Eye_Outer_04_ctrl', 'Left_Eye_Outer_05_ctrl', 'Left_Eye_Outer_06_ctrl', 'Left_Eye_Outer_07_ctrl', 'Left_Eye_Outer_08_ctrl']
DrivenList = ['Left_Eye_Inner_01_ctrl', 'Left_Eye_Inner_02_ctrl', 'Left_Eye_Inner_03_ctrl', 'Left_Eye_Inner_04_ctrl', 'Left_Eye_Inner_05_ctrl', 'Left_Eye_Inner_06_ctrl', 'Left_Eye_Inner_07_ctrl', 'Left_Eye_Inner_08_ctrl']
Influence_constraint(DriverList, DrivenList, AttrName, DefaultValue)