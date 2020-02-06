import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
from smbus2 import SMBus, i2c_msg

import time
from math import floor

def setup():
    GPIO.setup("P8_15", GPIO.OUT)
    GPIO.setup("P8_11", GPIO.OUT)
    GPIO.setup("P8_12", GPIO.OUT)
    GPIO.setup("P8_7", GPIO.OUT)
    GPIO.setup("P8_8",GPIO.OUT)    
    GPIO.setup("P9_41",GPIO.OUT)
    ADC.setup()
    
def clean():
    GPIO.cleanup()

def power_on():
    GPIO.output("P8_15", GPIO.LOW)
    time.sleep(0.1)
    GPIO.output("P8_11", GPIO.HIGH)
    print("+ ON")
    time.sleep(0.1)
    GPIO.output("P8_12", GPIO.HIGH)
    print("- ON")
    time.sleep(0.1)
    GPIO.output("P8_11", GPIO.LOW)
    time.sleep(0.1)
    GPIO.output("P8_12", GPIO.LOW)
    time.sleep(0.1)
    print("Amp Power ON")

def power_off():
    GPIO.output("P8_11", GPIO.LOW)
    time.sleep(0.1)
    GPIO.output("P8_12", GPIO.LOW)
    time.sleep(0.1)
    GPIO.output("P8_15", GPIO.HIGH)
    print("Amp Power OFF")
    
def heartbeat_pulse(t):
    GPIO.output("P8_7", GPIO.HIGH)
    time.sleep(t)
    GPIO.output("P8_7", GPIO.LOW)
    time.sleep(t)
    

def test_pulse(t):
    GPIO.output("P9_41", GPIO.HIGH)
    time.sleep(t)
    GPIO.output("P9_41", GPIO.LOW)
    time.sleep(t)
    
def test_on():
   GPIO.output("P8_8",GPIO.HIGH)

def test_off():
    GPIO.output("P8_8",GPIO.LOW)

def dump_ADC():
    for ii in range(7):
        value = 1.8*ADC.read("AIN"+str(ii))
        print("Channel {:d}: {:.3f}".format(ii,value))
        
def get_temp():
    voltage = 1.8*ADC.read("AIN5")
    return(-1481.96+(2.1962e6+(1.8639-voltage)/3.88e-6)**0.5)
    
def get_voltage_pos():
    voltage = 1.8*ADC.read("AIN2")
    return(voltage*5.5)
    
def get_voltage_neg():
    voltage = 1.8*ADC.read("AIN0")
    return(voltage*5.5)
    
    
def get_current_pos():
    voltage = 1.8*ADC.read("AIN4")
    return(voltage/0.225)
    
def get_current_neg():
    voltage = 1.8*ADC.read("AIN6")
    return(voltage/0.225)
    
    
def get_airflow():
    with SMBus(2) as bus:
        b=bus.read_word_data(0x60,0x43)
        time.sleep(0.1)
    return(b)
    
def get_airflow_temp():
    with SMBus(2) as bus:
        b=bus.read_word_data(0x60,0x47)
        time.sleep(0.1)
    return(b/100.)
    
def get_airflow_error():
    with SMBus(2) as bus:
        b=bus.read_byte_data(0x60,0x42)
        time.sleep(0.1)
    return(b)

def get_AMP_temp(slot,sensNum):
    addr=[0x14,0x16,0x26,0x34]
    msg=[0b10110010,0b10111010,0b10110011,0b10111011]
    data=read_LTC(addr[int(slot)-1],msg[int(sensNum)-1])
    return(( 1.8639 - data ) / (0.01177))

def get_channel_offset(slot,chanNum):
    addr=[0x14,0x16,0x26,0x34]
    msg=[0b10110100,0b10111100,0b10110101,0b10111101,0b10110110,0b10111110,0b10110111,0b10111111]
    data=read_LTC(addr[int(slot)-1],msg[int(chanNum)-1],0b10001111)
    return(data*1000./128.)
    
    
def set_serNum(slot,serNum):
    addr=[0x50,0x51,0x52,0x53]
    A=int(floor(serNum*2**-8))
    B=int(serNum-A*2**8)
    with SMBus(2) as bus:
        bus.write_byte_data(addr[int(slot-1)],0xf4,0)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf5,A)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf6,B)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf4,1)
        time.sleep(0.1)
    return(A*2**8+B)
    
def get_serNum(slot):
    addr=[0x50,0x51,0x52,0x53]
    with SMBus(2) as bus:
        A=bus.read_byte_data(addr[int(slot-1)],0xf5)
        time.sleep(0.1)
        B=bus.read_byte_data(addr[int(slot-1)],0xf6)
        time.sleep(0.1)
    return(A*2**8+B)
    
def get_channels_enable(slot):
    addr=[0x50,0x51,0x52,0x53]
    with SMBus(2) as bus:
        B=bus.read_byte_data(addr[int(slot-1)],0xf2)
        time.sleep(0.1)
    a=range(8)
    a.reverse()
    b=[0,0,0,0,0,0,0,0]
    for ii in a:
        b[ii]=int(floor(B/2**ii))
        B+=-b[ii]*2**ii
    return(b)
    
def set_channel_enable(slot,chan,en):
    b=get_channels_enable(slot)
    b[int(chan-1)]=int(en)
    B=0
    for ii in range(8):
        B+=b[ii]*2**ii
        
    addr=[0x50,0x51,0x52,0x53]
    with SMBus(2) as bus:
        bus.write_byte_data(addr[int(slot-1)],0xf4,0)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf2,B)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf4,1)
        time.sleep(0.1)
    return(b)

def get_AMP_alert(slot):
    addr=[0x50,0x51,0x52,0x53]
    with SMBus(2) as bus:
        B=bus.read_byte_data(addr[int(slot-1)],0xf3)
        time.sleep(0.1)
        return(1-B)
   
def set_AMP_alert_off(slot):
    addr=[0x50,0x51,0x52,0x53]
    with SMBus(2) as bus:
        bus.write_byte_data(addr[int(slot-1)],0xf4,0)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf3,1)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf4,1)
        time.sleep(0.1)

def set_AMP_alert_on(slot):
    addr=[0x50,0x51,0x52,0x53]
    with SMBus(2) as bus:
        bus.write_byte_data(addr[int(slot-1)],0xf4,0)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf3,0)
        time.sleep(0.1)
        bus.write_byte_data(addr[int(slot-1)],0xf4,1)
        time.sleep(0.1)
    

def read_LTC(addr,msg,cfg=0b10001000):
    # msg=0b10110010
    # addr=0x26
    write=i2c_msg.write(addr,[msg,cfg])
    read=i2c_msg.read(addr, 3)
    with SMBus(2) as bus:
        bus.i2c_rdwr(write)
        time.sleep(0.1)
        bus.i2c_rdwr(read)
        time.sleep(0.1)
    
    A=list(read)[0]
    B=list(read)[1]
    C=list(read)[2]
    
    if (A-2**7)>=0:
        A+=-2**7
        sgn=1
    else:
        sgn=0
    if A-2**6>=0:
        msb=1
        A+=-2**6
    else:
        msb=0
    
    out=A*2**10+B*2**2+C/2**6 
    out*=2**(-16)*2.5
    
    if sgn:
        if msb:
            out=999
    else:
        if msb:
            out+=-2.5
        else:
            out=-999
    return(out)
    
def switch_pos(slot_num):
    pos=['DDD','UDD','DUD','UUD']
    return(pos[slot_num-1])
    

    

    
    


