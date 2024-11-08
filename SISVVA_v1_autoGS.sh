#!/bin/bash

# Initialize parameters
SERVER_USER=""
SERVER_IP=""
SEQUENCE_NAME=""
SERVER_PASSWORD=""

# Parse values passed as parameters
while [[ $# -gt 0 ]]; do
    case $1 in
        -ip|--ip_address)
            SERVER_IP="$2"
            shift
            shift
            ;;
        -hn|--hostname)
            SERVER_USER="$2"
            shift
            shift
            ;;
        -sn|--sequence_name)
            SEQUENCE_NAME="$2"
            shift
            shift
            ;;
        -pw|--password)
            SERVER_PASSWORD="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if the required variables are set
if [[ -z "$SERVER_IP" || -z "$SERVER_USER" || -z "$SEQUENCE_NAME" || -z "$SERVER_PASSWORD" ]]; then
    echo "Usage: $0 -ip <ip_address> -hn <hostname> -sn <sequence_name> -pw <password>"
    exit 1
fi

# 1. Create remote folders and copy files
LOCAL_PATH="" # SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
REMOTE_PATH_BASE="/data/${SERVER_USER}/VCSR_sequences/${SEQUENCE_NAME}" # SET_TO_YOUR_REMOTE_SERVER_PATH
REMOTE_PATH_01="${REMOTE_PATH_BASE}/01_Original" # SET_TO_YOUR_REMOTE_SERVER_PATH
REMOTE_PATH_02="${REMOTE_PATH_BASE}/02_COLMAP" # SET_TO_YOUR_REMOTE_SERVER_PATH

echo "Creating remote folders..."
sshpass -p "$SERVER_PASSWORD" ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_PATH_01} ${REMOTE_PATH_02}"

echo "Copying files to remote folder..."
sshpass -p "$SERVER_PASSWORD" scp -r ${LOCAL_PATH}/* ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH_01}

# 2. Connect to the remote server via SSH and execute commands sequentially
# SET_TO_YOUR_REMOTE_SERVER_PATH
echo "Performing 3D reconstruction on the remote server..."
sshpass -p "$SERVER_PASSWORD" ssh -tt ${SERVER_USER}@${SERVER_IP} << EOF
    source /opt/anaconda3/etc/profile.d/conda.sh  # Modify the conda.sh path as needed
    conda activate gaussian_splatting
    /data3/${SERVER_USER}/Workspace/VCSR_auto/GS_recon_isyang.sh -sn ${SEQUENCE_NAME}
    exit
EOF

echo "Task completed!"
