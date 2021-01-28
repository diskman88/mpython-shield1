from mpython import i2c
from micropython import const
import time

MOTOR_1 = const(0x01)
"""
M1电机编号，0x01
"""

MOTOR_2 = const(0x02)
"""
M2电机编号，0x02
"""

_speed_buf = {}


def set_speed(motor_no, speed):
    """
    设置电机速度

    :param int motor_no: 控制电机编号，可以使用 ``MOTOR_1``, ``MOTOR_2`` ,或者直接写入电机编号。
    :param int speed: 电机速度，范围-100~100，负值代表反转。

    """
    global _speed_buf
    speed = max(min(speed, 100), -100)
    _speed_buf.update({motor_no: speed})
    attempts = 0
    while True:
        try:
            i2c.writeto(0x10, bytearray([motor_no, speed]))
        except Exception as e:
            attempts = attempts + 1
            time.sleep_ms(500)
            if attempts > 2:
                break
        else:
            break

def get_speed(motor_no):
    """
    返回电机速度

    :param int motor_no: 控制电机编号，可以使用 ``MOTOR_1``, ``MOTOR_2``,或者直接写入电机编号。
    :rtype: int
    :return: 返回该电机速度
    """
    global _speed_buf
    if motor_no in _speed_buf:

        return _speed_buf[motor_no]
    else:
        return None


def led_on(no, brightness=50):
    """
    打开灯。电机接口,除了可以驱动电机,还能做灯的控制。

    :param int no: 控制电机编号，可以使用 ``MOTOR_1``, ``MOTOR_2``,或者直接写入电机编号。
    :param int brightness: 设置亮度,范围0~100
    """
    brightness = max(min(brightness, 100), 0)
    attempts = 0
    while True:
        try:
            i2c.writeto(0x10, bytearray([no, brightness]))
        except Exception as e:
            attempts = attempts + 1
            time.sleep_ms(500)
            if attempts > 2:
                break
        else:
            break


def led_off(no):
    """
    关闭灯。

    :param int no: 控制电机编号，可以使用 ``MOTOR_1``, ``MOTOR_2``,或者直接写入电机编号。
    """
    attempts = 0
    while True:
        try:
            i2c.writeto(0x10, bytearray([no, 0]))
        except Exception as e:
            attempts = attempts + 1
            time.sleep_ms(500)
            if attempts > 2:
                break
        else:
            break

def get_battery_level():
    i2c.writeto(16, b'\x03')
    tmp = i2c.readfrom(16, 2)
    return struct.unpack('H', tmp)[0]


import struct

class IR_encode(object):
    def __init__(self):
        pass

    def encode_raw(self, carry_freq, len, repeat_pos, code, data):
        """
        制作任意编码。

        :param int carry_freq: 载波频率，单位hz。
        :param int len: 加上循环码后的单次发码的code总数
        :param int repeat_pos: 循环码位置
        :param int code: code列表，16个成员,记录8组不同的高低电平波形
        :param char data：编码波形数据，最长64字节
        """
        period = 1000000//carry_freq # us
        buff = struct.pack('>H2B', period*16, len, repeat_pos) # carry, len, repeat_pos
        i = 0
        _code = [0]*16
        while i < 8:
            _code[i] = code[i]//period
            _code[i+1] = code[i+1]//16
            i +=2
        # print(_code)
        for i in _code:
            buff += struct.pack('>H', i)
        for i in data:
            buff += struct.pack('B', i)

        return buff

    def encode_nec(self, user_code, command_code):
        '''
        :param int user_code: 用户码
        :param int command_code: 命令码
        '''
        buff = struct.pack('>H2B', 416, 36, 34) # carry, len, repeat_pos
        #              head    logic_1  logic_0  stop     repeat0   repeat1
        nec_code =  [346, 281, 22, 106, 22, 35, 22, 2437, 346, 140, 22, 6012, 0, 0, 0, 0]

        nec_key = [0]*36
        nec_key[0] = 0  # lead code
        for i in range(0, 8): # 把用户码转为code编号
            if (user_code >> i) & 0x01:
                nec_key[i+1] = 1
                nec_key[i+1+8] = 2
            else:
                nec_key[i+1] = 2
                nec_key[i+1+8] = 1 
            if (command_code >> i) & 0x01:
                nec_key[i+1+16] = 1
                nec_key[i+1+24] = 2
            else:
                nec_key[i+1+16] = 2
                nec_key[i+1+24] = 1
        nec_key[33] = 3
        nec_key[34] = 4
        nec_key[35] = 5
        # print(nec_key)

        # 计算stop bit低电平时间
        stopbit_low_time = 108000 - (9000 + 4500 + 2250*16 + 1120*16 + 560) #因为补码的原因，bit0 bit1数量各占16bit
        nec_code[7] = stopbit_low_time//16
        # print(nec_code)
        for i in nec_code:
            buff += struct.pack('>H', i)
        for i in nec_key:
            buff += struct.pack('B', i)
        
        # print(buff)
        return buff

class IR(object):
    def __init__(self):
        # self.buff = bytearray(118)
        pass

    def send(self, buff, repeat_en = 0):
        tmp = bytearray([0x04, repeat_en])
        tmp += buff
        # print(tmp)
        i2c.writeto(16, tmp)
        # self.check_buff(tmp)

    def stop_send(self):
        i2c.writeto(16, b'\x05')

    def start_learn(self):
        i2c.writeto(16, b'\x06')

    def get_learn_data(self):
        i2c.writeto(16, b'\x07')
        return i2c.readfrom(16, 118)

    def get_learn_status(self):
        i2c.writeto(16, b'\x08')
        return i2c.readfrom(16, 1)[0]

