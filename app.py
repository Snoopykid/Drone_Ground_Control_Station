from flask import Flask, render_template
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
import threading
import time

# .env 로드는 최상단에서 해야 함
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

master = None


def connect_mavlink(port='COM4', baud=57600):
    """MAVLink 드론 연결 시도. 실패 시 None 반환."""
    try:
        from pymavlink import mavutil
        conn = mavutil.mavlink_connection(port, baud=baud)
        conn.wait_heartbeat(timeout=10)
        print("Heartbeat from system (system %u component %u)" % (
            conn.target_system, conn.target_component))
        return conn
    except Exception as e:
        print(f"[MAVLink] 연결 실패: {e}")
        return None


def drone_telemetry_thread():
    """백그라운드 스레드: 드론 텔레메트리를 주기적으로 읽어 SocketIO로 브로드캐스트."""
    global master
    master = connect_mavlink()

    while True:
        if master is None:
            time.sleep(5)
            master = connect_mavlink()
            continue

        try:
            msg = master.recv_match(
                type=['GLOBAL_POSITION_INT', 'SYS_STATUS', 'GPS_RAW_INT'],
                blocking=True,
                timeout=2
            )
            if msg is None:
                continue

            msg_type = msg.get_type()

            if msg_type == 'GLOBAL_POSITION_INT':
                # lat/lon은 1e7 스케일로 저장됨
                data = {
                    'type': 'position',
                    'lat': msg.lat / 1e7,
                    'lon': msg.lon / 1e7,
                    'alt': msg.alt / 1000.0,           # mm → m
                    'relative_alt': msg.relative_alt / 1000.0,
                }
                socketio.emit('drone_data', data)

            elif msg_type == 'SYS_STATUS':
                data = {
                    'type': 'status',
                    'battery': msg.battery_remaining,   # % (-1이면 알 수 없음)
                    'voltage': msg.voltage_battery / 1000.0,  # mV → V
                }
                socketio.emit('drone_data', data)

            elif msg_type == 'GPS_RAW_INT':
                data = {
                    'type': 'gps',
                    'fix_type': msg.fix_type,           # 3 = 3D Fix (정상)
                    'satellites_visible': msg.satellites_visible,
                }
                socketio.emit('drone_data', data)

        except Exception as e:
            print(f"[MAVLink] 데이터 수신 오류: {e}")
            master = None  # 연결 끊김 → 재연결 유도
            time.sleep(2)


@socketio.on('connect')
def handle_connect():
    print("Client connected")
    socketio.emit('server_response', {'value': 'GCS 서버 연결됨'})


@app.route('/')
def home():
    API_key = os.getenv('API_key', '')
    return render_template('index.html', API_key=API_key)


if __name__ == '__main__':
    # daemon=True: 메인 프로세스 종료 시 스레드도 함께 종료
    t = threading.Thread(target=drone_telemetry_thread, daemon=True)
    t.start()

    # app.run() 대신 socketio.run() 사용해야 WebSocket이 정상 동작
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)
