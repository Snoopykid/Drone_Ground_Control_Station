from pymavlink import mavutil
from flask import Flask, render_template
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
import threading
import time

# 시리얼 포트 연결 설정 (예: COM4 포트에서 57600 baud rate로 통신)
master = mavutil.mavlink_connection('COM4', baud=57600)




# 연결이 수립될 때까지 기다리기
master.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (master.target_system, master.target_component))




load_dotenv()

# 예: 드론의 현재 위치 요청
master.mav.command_long_send(
    master.target_system, 
    master.target_component, 
    mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE, 
    0, 
    mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 0, 0, 0, 0, 0, 0
)

# 데이터 수신 및 출력
msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
if msg:
    print("Lat: %d, Lon: %d, Alt: %d" % (msg.lat, msg.lon, msg.alt))
    
    
# #Flask 함수라인
app = Flask(__name__)
socketio = SocketIO(app)

# 서버에서 클라이언트로 주기적으로 데이터 전송
@socketio.on('connect')
def handle_connect():
    print("Client connected")


@app.route('/')
def home():
    API_key = os.getenv('API_key')
    return render_template('index.html', API_key=API_key)  # index.html 렌더링

if __name__ == '__main__':
    app.run('127.0.0.1',port=5000,debug=False)