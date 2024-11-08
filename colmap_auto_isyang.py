import subprocess
import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import shutil  # Modification: Added shutil module

# SET_TO_YOUR_PATH
usage_text = '''Usage:
  python colmap_auto_isyang.py -ip /path/to/images -wp /path/to/workspace -sn sequence_name

Option Description:
  -ip, --image_path       Specify the directory path where input images are stored.
  -wp, --workspace_path   Specify the workspace directory path. Result files and intermediate files will be saved here.
  -sn, --sequence_name    Specify the sequence name to use for naming the database file.

Example:
  python colmap_auto_isyang.py -ip ../Resources/2_Original_target/ -wp ../Resources/5_Parameters/ -sn VRroom1
'''

parser = argparse.ArgumentParser(
    description='COLMAP Automatic Reconstruction Script',
    formatter_class=argparse.RawTextHelpFormatter,
    add_help=False
)

parser.add_argument('-h', '--help', action='help', help='Show this help message and exit\n\n' + usage_text)
parser.add_argument('-ip', '--image_path', required=True, help='Input image directory path')
parser.add_argument('-wp', '--workspace_path', required=True, help='Workspace directory path')
parser.add_argument('-sn', '--sequence_name', required=True, help='Sequence name for naming the database file')
args = parser.parse_args()

# Input image directory
image_path = os.path.abspath(args.image_path)

# Workspace and output directory
workspace_path = os.path.abspath(args.workspace_path)

# Sequence name
sequence_name = args.sequence_name

# Database directory (workspace_path)
database_path = os.path.join(workspace_path, f"{sequence_name}.db")

# Model & results saving directory
sparse_model_path = os.path.join(workspace_path, 'sparse/0/')
dense_model_path = os.path.join(workspace_path, 'dense/')  # Note: Variable position maintained
exported_ply_path = os.path.join(workspace_path, 'exported/')

# COLMAP executable file directory
colmap_executable = 'colmap'
# If COLMAP is included in system PATH, leave it as it is
# If not, please enter the full path.

# 1. Database setup and feature extraction
def set_project():
    subprocess.run([
        colmap_executable, "feature_extractor",
        "--database_path", database_path,
        "--image_path", image_path,
        "--SiftExtraction.use_gpu", "1",  # Set GPU usage (set to 0 if no CUDA)
        "--ImageReader.camera_model", "PINHOLE",  # Set camera model
        "--SiftExtraction.max_image_size", "2000"  # Set maximum image size limit
    ], check=True)
    print("Feature extraction completed with GPU (Camera model: PINHOLE)")

# 2. Feature matching
def feature_matching():
    # Exhaustive Matcher
    subprocess.run([
        colmap_executable, "exhaustive_matcher",
        "--database_path", database_path
    ], check=True)
    print("Exhaustive feature matching completed")

# 3. Sparse reconstruction
def sparse_reconstruction():
    # Incremental Mapper
    subprocess.run([
        colmap_executable, "mapper",
        "--database_path", database_path,
        "--image_path", image_path,
        "--output_path", sparse_model_path
    ], check=True)
    print("Sparse reconstruction completed")

# 4. Dense reconstruction
def dense_reconstruction():
    # Modification start: Delete existing dense directory
    if os.path.exists(dense_model_path):
        shutil.rmtree(dense_model_path)
    os.makedirs(dense_model_path, exist_ok=True)
    # Modification end

    # Stereo matching
    subprocess.run([
        colmap_executable, "image_undistorter",
        "--image_path", image_path,
        "--input_path", sparse_model_path,
        "--output_path", dense_model_path,
        "--output_type", "COLMAP"
    ], check=True)
    subprocess.run([
        colmap_executable, "patch_match_stereo",
        "--workspace_path", dense_model_path,
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.geom_consistency", "true",
        "--PatchMatchStereo.gpu_index", "0"  # Set GPU index (0 for the first GPU)
    ], check=True)
    # Fusion
    subprocess.run([
        colmap_executable, "stereo_fusion",
        "--workspace_path", dense_model_path,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", os.path.join(dense_model_path, 'fused.ply')
    ], check=True)
    print("Dense reconstruction completed with GPU")

# 5. Sparse point cloud export
def export_sparse_point_cloud():
    # Create export directory
    os.makedirs(exported_ply_path, exist_ok=True)

    sparse_ply_path = os.path.join(exported_ply_path, f"{sequence_name}_sparse_points3D.ply")
    subprocess.run([
        colmap_executable, "model_converter",
        "--input_path", sparse_model_path,
        "--output_path", sparse_ply_path,
        "--output_type", "PLY"
    ], check=True)
    print(f"Sparse point cloud saved at {sparse_ply_path}")

# 6. Dense point cloud export
def export_dense_point_cloud():
    dense_fused_ply = os.path.join(dense_model_path, "fused.ply")

    # Check whether dense point cloud file exists
    if os.path.exists(dense_fused_ply):
        target_path = os.path.join(exported_ply_path, f"{sequence_name}_dense_fused.ply")
        os.makedirs(exported_ply_path, exist_ok=True)

        # Copy dense point cloud file
        subprocess.run(["cp", dense_fused_ply, target_path], check=True)
        print(f"Dense point cloud file saved at {target_path}")
    else:
        print("fused.ply file does not exist. Please check if dense reconstruction was successful.")

# 7. Camera parameter visualization
def visualize_camera_parameters():
    # Convert model to text format
    temp_model_path = os.path.join(workspace_path, 'sparse_text')
    os.makedirs(temp_model_path, exist_ok=True)
    subprocess.run([
        colmap_executable, "model_converter",
        "--input_path", sparse_model_path,
        "--output_path", temp_model_path,
        "--output_type", "TXT"
    ], check=True)

    # Read cameras.txt and images.txt
    cameras_file = os.path.join(temp_model_path, 'cameras.txt')
    images_file = os.path.join(temp_model_path, 'images.txt')

    cameras = {}
    with open(cameras_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            elems = line.strip().split()
            if len(elems) >= 5:
                camera_id = int(elems[0])
                model = elems[1]
                width = int(elems[2])
                height = int(elems[3])
                params = list(map(float, elems[4:]))
                cameras[camera_id] = {
                    'model': model,
                    'width': width,
                    'height': height,
                    'params': params
                }
    images = {}
    with open(images_file, 'r') as f:
        lines = f.readlines()
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if line.startswith('#'):
                idx += 1
                continue
            elems = line.strip().split()
            if len(elems) >= 9:
                image_id = int(elems[0])
                qvec = np.array(list(map(float, elems[1:5])))
                tvec = np.array(list(map(float, elems[5:8])))
                camera_id = int(elems[8])
                image_name = ' '.join(elems[9:])  # Handle image names with spaces
                images[image_id] = {
                    'qvec': qvec,
                    'tvec': tvec,
                    'camera_id': camera_id,
                    'image_name': image_name
                }
                idx += 2  # Skip the next line containing 2D points
            else:
                idx += 1

    # Visualization
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for image_id, image_data in images.items():
        qvec = image_data['qvec']
        tvec = image_data['tvec']
        R = qvec2rotmat(qvec)
        camera_center = -R.T @ tvec

        ax.scatter(camera_center[0], camera_center[1], camera_center[2], c='r', marker='o')
        ax.text(camera_center[0], camera_center[1], camera_center[2], f'Cam{image_id}', color='blue')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Save the visualization as an image file
    visualization_output_path = os.path.join(exported_ply_path, f"{sequence_name}_camera_parameters_visualization.png")
    plt.savefig(visualization_output_path)
    plt.close(fig)
    print(f"Camera parameters visualization saved at {visualization_output_path}")

def qvec2rotmat(qvec):
    q0, q1, q2, q3 = qvec
    R = np.array([
        [1 - 2 * q2**2 - 2 * q3**2,     2 * q1 * q2 - 2 * q0 * q3,     2 * q1 * q3 + 2 * q0 * q2],
        [    2 * q1 * q2 + 2 * q0 * q3, 1 - 2 * q1**2 - 2 * q3**2,     2 * q2 * q3 - 2 * q0 * q1],
        [    2 * q1 * q3 - 2 * q0 * q2,     2 * q2 * q3 + 2 * q0 * q1, 1 - 2 * q1**2 - 2 * q2**2]
    ])
    return R

# Workflow execution
if __name__ == "__main__":
    # Create workspace directory
    os.makedirs(workspace_path, exist_ok=True)

    set_project()
    feature_matching()
    sparse_reconstruction()
    export_sparse_point_cloud()
    dense_reconstruction()
    export_dense_point_cloud()
    visualize_camera_parameters()
