#!/bin/bash

# Parameter 초기화
SERVER_USER=""
SERVER_IP=""
SEQUENCE_NAME=""
SERVER_PASSWORD=""

# Parameter로 전달된 값들을 파싱
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
            echo "알 수 없는 옵션: $1"
            exit 1
            ;;
    esac
done

# 필수 변수들이 설정되었는지 확인
if [[ -z "$SERVER_IP" || -z "$SERVER_USER" || -z "$SEQUENCE_NAME" || -z "$SERVER_PASSWORD" ]]; then
    echo "사용법: $0 -ip <ip_address> -hn <hostname> -sn <sequence_name> -pw <password>"
    exit 1
fi

# 1. 원격 폴더 생성 및 파일 복사
LOCAL_PATH="" #SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
REMOTE_PATH_BASE="/data/${SERVER_USER}/VCSR_sequences/${SEQUENCE_NAME}" #SET_TO_YOUR_REMOTE_SERVER_PATH
REMOTE_PATH_01="${REMOTE_PATH_BASE}/01_Original" #SET_TO_YOUR_REMOTE_SERVER_PATH
REMOTE_PATH_02="${REMOTE_PATH_BASE}/02_COLMAP" #SET_TO_YOUR_REMOTE_SERVER_PATH

echo "원격 폴더 생성 중..."
sshpass -p "$SERVER_PASSWORD" ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_PATH_01} ${REMOTE_PATH_02}"

echo "파일을 원격 폴더로 복사 중..."
sshpass -p "$SERVER_PASSWORD" scp -r ${LOCAL_PATH}/* ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH_01}

# 2. SSH를 통해 원격 서버에 접속 후 명령을 연속으로 실행
echo "원격 서버에서 3차원 재구성 수행 중..."
sshpass -p "$SERVER_PASSWORD" ssh -tt ${SERVER_USER}@${SERVER_IP} << EOF
    source /opt/anaconda3/etc/profile.d/conda.sh  # conda.sh 경로 수정 필요
    conda activate gaussian_splatting
    /data3/${SERVER_USER}/Workspace/VCSR_auto/GS_recon_isyang.sh -sn ${SEQUENCE_NAME}
    exit
EOF

echo "작업 완료!"
