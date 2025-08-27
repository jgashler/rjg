import maya.cmds as mc
import json

def CleanImport(POSE_FILE):
    # Load plugin if not loaded
    if not mc.pluginInfo("MayaUERBFPlugin", query=True, loaded=True):
        mc.loadPlugin("MayaUERBFPlugin")
        print("Loaded MayaUERBFPlugin.")

    # Import the pose wrangler API
    from epic_pose_wrangler.v2 import main
    rbf_api = main.UERBFAPI(view=False)

    # Read pose file once
    with open(POSE_FILE, 'r') as f:
        pose_data = json.load(f)

    solvers_in_file = list(pose_data.get("solvers", {}).keys())
    print("Solvers listed in file:", solvers_in_file)

    # Delete existing solvers from scene before importing
    for solver_name in solvers_in_file:
        if mc.objExists(solver_name):
            mc.delete(solver_name)
            print(f"Deleted existing solver: {solver_name}")

    # Import solvers and all poses from file fresh
    try:
        rbf_api.deserialize_from_file(POSE_FILE)
        print("\n✅ Successfully imported all pose data.")
    except Exception as e:
        print(f"❌ Failed to import pose data: {e}")
