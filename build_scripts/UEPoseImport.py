import maya.cmds as mc
import os
import json

def CleanImport(POSE_FILE):
    # Make sure the plugin is loaded
    if not mc.pluginInfo("MayaUERBFPlugin", query=True, loaded=True):
        mc.loadPlugin("MayaUERBFPlugin")
        print("Loaded MayaUERBFPlugin.")

    # Path to the pose file
    #POSE_FILE = r"G:/bobo/character/Rigs/Susaka/Poses/Poses_01.json"

    # Import your RBF API
    from epic_pose_wrangler.v2 import main
    rbf_api = main.UERBFAPI(view=False)

    # --- Load data from file just once
    with open(POSE_FILE, 'r') as f:
        pose_data = json.load(f)

    solvers_in_file = list(pose_data.get("solvers", {}).keys())
    print("Solvers listed in file:", solvers_in_file)

    # Iterate through solvers from the file, rebuild and load them
    for solver_name in solvers_in_file:
        print("\n--- Processing Solver:", solver_name)
            solver_data = pose_data["solvers"][solver_name]
            print("Solver data keys:", list(solver_data.keys()))
            print("Solver data:", solver_data)

        # Delete existing solver if present
        if mc.objExists(solver_name):
            mc.delete(solver_name)
            print(f"Deleted existing solver: {solver_name}")

        # Get associated drivers from the JSON
        drivers = pose_data["solvers"][solver_name].get("inputsControllers", [])
        if not drivers:
            print(f"⚠️ No drivers found for solver {solver_name} in file.")
            continue

        # Create new solver with drivers
        try:
            rbf_api.create_rbf_solver(solver_name=solver_name, drivers=drivers)
            print(f"Created solver: {solver_name} with drivers: {drivers}")
        except Exception as e:
            print(f"❌ Failed to create solver {solver_name}:", e)
            continue

    # Now that all solvers are re-initialized, import the pose data
    try:
        rbf_api.deserialize_from_file(POSE_FILE)
        print("\n✅ Successfully imported all pose data.")
    except Exception as e:
        print("❌ Failed to import pose data:", e)
