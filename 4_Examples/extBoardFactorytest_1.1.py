from mpython import *
import parrot
from machine import Timer

volt = ADC(Pin(Pin.P0))


# 喇叭测试
def speaker():
    p8 = PWM(Pin(Pin.P8), freq=1000, duty=512)
    p9 = PWM(Pin(Pin.P9), freq=1000, duty=512)
    sleep(2)
    p8.duty(0)
    p9.duty(0)
    p8 = PWM(Pin(Pin.P8), freq=0, duty=512)
    for i in range(20, 20000, 200):
        p8.freq(i)
        print(i)
        sleep_ms(20)
    p8.duty(0)
    sleep_ms(200)
    p9 = PWM(Pin(Pin.P9), freq=20000, duty=512)
    for i in range(20000, 20, -200):
        p9.freq(i)
        print(i)
        sleep_ms(20)
    p9.duty(0)
    sleep_ms(200)
    sleep(1)
    p8.duty(0)
    p9.duty(0)


dc_status = False


def driver_test(_):

    global dc_status
    if dc_status:
        parrot.set_speed(parrot.MOTOR_1, 100)
        parrot.set_speed(parrot.MOTOR_2, 100)
    else:
        parrot.set_speed(parrot.MOTOR_1, -100)
        parrot.set_speed(parrot.MOTOR_2, -100)
    dc_status = not dc_status


rgb.fill((
    0,
    0,
    0,
))
rgb.write()

oled.DispChar("扬声器测试", 40, 15)
oled.DispChar("1KHz信号+扫频", 20, 30)

oled.show()
speaker()

oled.fill(0)
tim1 = Timer(1)

tim1.init(period=2000, mode=Timer.PERIODIC, callback=driver_test)

while True:
    value = volt.read() * 3.3 / 4095
    oled.DispChar("电机：2秒循环正反转", 0, 0)
    oled.DispChar("电压值：%0.2f" % value, 0, 20)
    oled.DispChar("usb接口:用usb电流表", 0, 35)
    oled.show()
