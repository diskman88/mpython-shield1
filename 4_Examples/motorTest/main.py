from mpython import *
from shield import *
import time
import struct

# test
ir_code = IR_encode()
ir = IR()

# 示例1 发送NEC编码
# 参数1：用户码 参数2：命令码
ir_buff = ir_code.encode_nec(0x01,0x55)
while True:
    ir.send(ir_buff, repeat_en = 1)
    time.sleep_ms(3000)
    ir.stop_send()
    time.sleep_ms(3000)
    # set_speed(1,100)
    # set_speed(2,100)
    # time.sleep_ms(2000)
    # set_speed(1,-100)
    # set_speed(2,-100)
    # time.sleep_ms(2000)

# 示例2 编码学习
key_pressed = False
key_pressed1 = False

def on_button_b_down(_):
    global key_pressed
    time.sleep_ms(10)
    if button_b.value() == 1: return
    key_pressed = True

button_b.irq(trigger=Pin.IRQ_FALLING, handler=on_button_b_down)

def on_button_a_down(_):
    global key_pressed1
    time.sleep_ms(10)
    if button_a.value() == 1: return
    key_pressed1 = True

button_a.irq(trigger=Pin.IRQ_FALLING, handler=on_button_a_down)

buff = bytearray()
learn_successed = False

while True:
    if key_pressed:
        key_pressed = False      
        rgb[0] = (int(255), int(0), int(0))
        rgb.write()
        ir.start_learn()
        time.sleep(4) # 须在4秒内按住遥控灯灭后松开
        rgb[0] = (int(0), int(0), int(0))
        rgb.write()
        status = ir.get_learn_status()
        if(status == 0): # 学习成功
            buff = ir.get_learn_data() # 获取学习的按键参数。
            learn_successed = True
            oled.fill(0)
            oled.DispChar('success.', 10, 10, 1)
            oled.show()
            print(struct.unpack('>H2B16H', buff))
            # print(buff)
        else:
            learn_successed = False
            oled.fill(0)
            oled.DispChar('false.', 10, 10, 1)
            oled.show()
    # print(learn_successed)
    if key_pressed1:
        key_pressed1 = False;
        print("send")
        if learn_successed:
            ir.send(buff, 1)  # 利用学到的按键参数发码。
            time.sleep_ms(1000)
            ir.stop_send()
      
# 示例3：发送philip RC-6编码（暂有问题，时序整理有问题）
#           lead
# MN6014_C5D6_code = [3376, 3376, 844, 844, 844, 1688, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# MN6014_C5D6_data = [0, 
#                     1, 1, 1, 1, 2, 
#                     1, 1, 1, 1, 1, 2, 
#                     2, 2, 2, 2, 1, 
#                     2, 2, 2, 2, 2, 1, 
#                     ]
# buff = ir_code.encode_raw(38000, 23, 22, MN6014_C5D6_code, MN6014_C5D6_data)
# while True:
#     ir.send(buff)
#     time.sleep_ms(200)

# def start():
#     rgb[0] = (int(255), int(0), int(0))
#     rgb.write()
#     ir.start_learn()
#     time.sleep(4) # 须在4秒内按住遥控灯灭后松开
#     rgb[0] = (int(0), int(0), int(0))
#     rgb.write()
#     status = ir.get_learn_status()
#     print(status)
