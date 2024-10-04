from flask import Flask
# Import common module for MAVLink 2
from pymavlink.dialects.v20 import common as mavlink2
import serial


# #serial 함수 라인
# ser = serial.Serial('COM1', 9600)  # Windows에서
# # 또는
# # ser = serial.Serial('/dev/ttyUSB0', 9600)  # Linux에서

#Flask 함수라인
app = Flask(__name__)

@app.route('/')
def home():
    return 'This is Home!'

if __name__ == '__main__':
    app.run('127.0.0.1',port=5000,debug=True)