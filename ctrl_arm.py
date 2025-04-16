import serial
import time

def open_serial(port, baudrate, timeout):
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print("Port opened successfully.")
        return ser
    except Exception as e:
        print(f"Failed to open port: {e}")
        exit()

def send_command(ser, command):
    if not command.endswith("\n"):
        command += "\n"  # 명령어 끝에 개행 문자 추가
    ser.write(command.encode())
    print(f"Sent command: {repr(command)}")

    response = ser.readline()  # 응답 읽기
    print(f"Raw response: {response}")
    if response:
        try:
            print(f"Decoded response: {response.decode('utf-8')}")
        except UnicodeDecodeError:
            print(f"Non-UTF-8 response: {response}")
    else:
        print("No response received.")

def main():
    # Serial 포트 설정
    port = "/dev/ttyUSB0"  # 연결된 포트
    baudrate = 115200      # Baudrate 설정
    timeout = 2            # Timeout 설정
    ser = open_serial(port, baudrate, timeout)

    # 명령 루프 시작
    while True:
        try:
            user_input = input("\nInput command (or type 'quit' to exit): ")
            if user_input.lower() == "quit":
                print("Exiting...")
                break

            # 명령어 전송
            send_command(ser, user_input)
            time.sleep(0.5)  # 대기 시간 추가
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Error during communication: {e}")

    # Serial 포트 닫기
    try:
        ser.close()
        print("Serial port closed.")
    except Exception as e:
        print(f"Error closing serial port: {e}")

if __name__ == "__main__":
    main()
