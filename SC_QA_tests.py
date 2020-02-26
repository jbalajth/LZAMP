"""
Created on Tue Jan 14 2020
author: jyothisjohnson
"""

import LZAMP_CTRL as lzamp
from time import sleep, time
from threading import Thread, Event
import sys
from os.path import isfile
from csv import DictWriter

def loop_heartbeat():
    try:
        print('SC heartbeat started')
        while (not event.is_set()):
            lzamp.heartbeat_pulse(2)
        print('SC heartbeat stopped')
    except:
        error.set()
        print('ERROR: heartbeat failure')

def loop_test():
    try:
        print('test pulse started')
        while (not event.is_set()):
            lzamp.test_pulse(0.1)
        print('test pulse stopped')
    except:
        error.set()
        print('ERROR: test loop failure')

def check_input_yn(question):
    tmp='n'
    while not tmp=='y':
        tmp=raw_input((question))
        if tmp=='n':
            return(True)
        elif not tmp=='y':
            print('try again')
    return(False)


if __name__ == '__main__':
    
    event=Event()
    complete=Event()
    error=Event()
    lzamp.setup()
    lzamp.power_off()
    lzamp.test_on()
    
    if check_input_yn('\nHas last two digits of serial number been hand-written on the control board? (y/n) '):   
        print('fatal error, exiting.')
        exit()
        
    try:
        tester=raw_input('Enter name of tester: ')
        date=raw_input('Enter date: (MM/DD/YYYY) ')
        tstart=raw_input('Enter start time in 24-hour format: (1:17 pm would be 1317) ')
        temperature=float(raw_input('Enter current room temperature as read by thermometer: (Celsius) '))
        SC_serNum=int(raw_input('Enter serial number: (Note: for serial number begining with 0, enter single digit) '))
        
        fname='QA_Test_SC_Board_{:d}.txt'.format(int(SC_serNum))
        print('data logging started under file name: '+fname)
        with open(fname,'w+') as f:
            f.write(("QA test for SC board: {:d}. Tested by "+tester+" beginning on "+date+
                    " at "+tstart+".\n\n").format(SC_serNum))
            f.write("Room Temperature Recorded as: {:.4g}.\n".format(temperature))
            
            SC_temp=lzamp.get_temp()
            f.write("SC Board Temperature Recorded as: {:.4g}.\n".format(SC_temp))
            
            
            serNums=[509,510,602,113] #Modify if amplifier boards are changed out
            print("Checking I2C communication by getting serial numbers.")
            for slot in range(1,5):
                tmp=lzamp.get_serNum(slot)
                if not (tmp==serNums[slot-1]):
                    print('fatal error, error getting serial numbers, exiting.')
                    exit()
            print('I2C comunication established.\n')
            f.write("PASSED I2C communication test.\n")
        
            if check_input_yn('\nAre green lights off on all amp boards? (y/n) '):   
                print('fatal error, exiting.')
                exit()
            
            c_neg_off=lzamp.get_current_neg()
            c_pos_off=lzamp.get_current_pos()
            
            if c_neg_off > 0.5 or c_pos_off > 0.5:
                print('Current readings are too high when amps are powered off. Exiting...')
                exit()

            lzamp.power_on()
        
            if check_input_yn('\nAre green lights now lit on all amp boards? (y/n) '):   
                print('fatal error, exiting.')
                exit()
            
            lzamp.power_off()
            
            
            if check_input_yn('\nAre green lights off on all amp boards? (y/n) '):   
                print('fatal error, exiting.')
                exit()
            
            c_neg_off=lzamp.get_current_neg()
            c_pos_off=lzamp.get_current_neg()

            if c_neg_off > 0.5 or c_pos_off > 0.5:
                print('Current readings are too high when amps are powered off. Exiting...')
                exit()

            lzamp.power_on()
            
            if check_input_yn('\nAre green lights now lit on all amp boards? (y/n) '):   
                print('fatal error, exiting.')
                exit()
            print('Power Cycle Successful.\n')
            print('No current recorded when amps powered off.\n')
            f.write("PASSED Power Cycle Test.\n")
            f.write('PASSED Current Check When Amps Were Powered Off.\n')
            
            
            t=Thread(target=loop_heartbeat)
            t.start()
            sleep(1)
            
            if check_input_yn('\nIs the heartbeat pulse flashing? (y/n) '): 
                print('fatal error, exiting. Heartbeat pulse LED not flashing.')
                event.set()
                t.join()
                exit()
                    
            event.set()
            t.join()
            event.clear()
            
            print('Heartbeat Pulse Test Successful.\n')
            f.write("PASSED Heartbeat Pulse Test.\n")
        
            t=Thread(target=loop_test)
            t.start()
            sleep(1)
            
            if check_input_yn('\nIs the test pulse showing on oscilloscope? (y/n) '): 
                print('fatal error, exiting. Test pulse not showing on oscilloscope.')
                event.set()
                t.join()
                exit()
                    
            lzamp.test_off()

            if check_input_yn('\nIs test pulse no longer showing on the oscilloscope? (y/n) '):
                print('fatal error, exiting. Test pulse still showing on oscilloscope.')
                event.set()
                t.join()
                exit()
            
            lzamp.test_on()

            if check_input_yn('\nIs the test pulse now showing on oscilloscope? (y/n) '): 
                print('fatal error, exiting. Test pulse not showing on oscilloscope.')
                event.set()
                t.join()
                exit()

            event.set()
            t.join()
            event.clear()    
            
            print('Test Pulse Successfully Sent to AMP Boards.\n')
            print('Test Enable/Disable Successfully Checked.\n')
            f.write("Test Pulse Successfully Sent to AMP Boards.\n")
            f.write("Test Enable/Disable Option Successfully Checked.\n")
            
            current_pos=lzamp.get_current_pos()
            current_neg=lzamp.get_current_neg()
            volt_pos=lzamp.get_voltage_pos()
            volt_neg=lzamp.get_voltage_neg()
            
            print('Current and Voltage Readings Obtained Successfully.\n')
            f.write("Pos_Current: {:.4g}\tNeg_Current: {:.4g}\nPos_Voltage: {:.4g}\tNeg_Voltage: {:.4g}\n".format(
                    current_pos,current_neg,volt_pos,volt_neg))
        
        write_str='{:.4g}, '
        if not isfile('SC_voltage_current_recordings.csv'):
            with open('SC_voltage_current_recordings.csv','a+') as g:
                g.write("SC_Board_num,Room Temp,SC Board Temp,Positive Voltage,Positive Current,Negative Voltage,Negative Current\n")
        with open('SC_voltage_current_recordings.csv','a+') as g:
            g.write(write_str.format(SC_serNum))
            g.write(write_str.format(temperature))                
            g.write(write_str.format(SC_temp))
            g.write(write_str.format(volt_pos))
            g.write(write_str.format(current_pos))
            g.write(write_str.format(volt_neg))
            g.write(write_str.format(current_neg))
            g.write('\n')
       
        complete.set()     
    except:
        print('data logging failed')
        error.set()
    
    lzamp.power_off()
    lzamp.test_off()
    
    if (error.is_set()):
        print('\nTerminated on error condition')
    elif (complete.is_set()):
        print('Slow Control QA Test Completed Successfully')
