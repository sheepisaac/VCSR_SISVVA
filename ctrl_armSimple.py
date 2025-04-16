import serial
import time

def open_serial(port, baudrate, timeout):
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print("✅ Serial port opened successfully.")
        return ser
    except Exception as e:
        print(f"❌ Failed to open serial port: {e}")
        exit()

def send_command(ser, x, y, z, t, spd=0.75):
    cmd = f'{{"T":104,"x":{x},"y":{y},"z":{z},"t":{t},"spd":{spd}}}\n'
    ser.write(cmd.encode())
    print(f"➡️ Sent command: {cmd.strip()}")

    response = ser.readline()
    if response:
        try:
            print("⬅️ Response:", response.decode('utf-8').strip())
        except UnicodeDecodeError:
            print("⚠️ Non-UTF8 response:", response)

def main():
    port = "/dev/ttyUSB0"  # 필요 시 ttyAMA0 으로 변경
    baudrate = 115200
    timeout = 2
    ser = open_serial(port, baudrate, timeout)

    print("🦾 Input x, y, z, t values to control the arm.")
    print("📌 Format: x y z t (e.g., 100 0 480 4.1)")
    print("⛔ Type 'quit' to exit.")

    while True:
        try:
            user_input = input("\nInput x, y, z, t: ")
            if user_input.strip().lower() == 'quit':
                print("👋 Exiting...")
                break

            parts = user_input.strip().split()
            if len(parts) != 4:
                print("⚠️ Please enter exactly 4 values (x y z t).")
                continue

            x, y, z, t = map(float, parts)
            send_command(ser, x, y, z, t)

        except KeyboardInterrupt:
            print("\n👋 Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    try:
        ser.close()
        print("🔌 Serial port closed.")
    except Exception as e:
        print(f"⚠️ Error closing serial port: {e}")

if __name__ == "__main__":
    main()
