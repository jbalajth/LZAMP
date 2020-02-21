"""
Created on Wed Feb 5 13:20 2020

@author: jyothisjohnson
"""

import LZAMP_CTRL as lzamp
from time import sleep, localtime
from datetime import date
from threading import Thread, Event, Lock
from os.path import isfile
from numpy import zeros, absolute
import sys
import logging


def setup_logger(name, log_file, level=logging.DEBUG):
    handler = logging.FileHandler(log_file, mode='a')        
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

#def check_input_yn(question):
#    tmp='n'
#    while not tmp=='y':
#        tmp=raw_input((question))
#        if tmp=='n':
#            return(True)
#        elif not tmp=='y':
#            print('try again')
#    return(False)

def loop_heartbeat():
    try:
        while (not end_log.is_set()):
            lzamp.heartbeat_pulse(2)
    
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass
    
def set_board_enable(slot,en):
    for ch in range(8):
        lzamp.set_channel_enable(slot,ch+1,en)

def get_board_status(slot):
    tmp=lzamp.get_channels_enable(slot)
    if sum(tmp)!=0:
        return 1
    else:
        return 0

def get_channel_status(slot, ch):
    tmp= lzamp.get_channels_enable(slot)[ch-1]
    return tmp

def get_channel_enabled_count():
    tmp=0
    for ii in range(4):
        tmp+=sum(lzamp.get_channels_enable(ii+1))
    return tmp

#def loop_channel_disable(slot,ch):
#    try:
#        while (not end_log.is_set()):
#            sleep(1)
#            channel_lock.acquire()
#            if globals()['board_%s_ch_%s_disable' %(slot,ch)].is_set():
#                lzamp.set_channel_enable(slot,ch,0)
#            elif (not globals()['board_%s_ch_%s_disable' %(slot,ch)].is_set())&(get_channel_status(slot,ch)==0):
#                lzamp.set_channel_enable(slot,ch,1)
#            channel_lock.release()
#    except:
#        error.set()
#        print('ERROR: failure with enabling/disabling channel')
    
def channel_disabler(slot, ch):
    try:
        if globals()['board_%s_ch_%s_disable' %(slot,ch)].is_set()&(get_channel_status(slot,ch)==1):
            lzamp.set_channel_enable(slot,ch,0)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass

def channel_enabler(slot, ch):
    try:
        if (not globals()['board_%s_ch_%s_disable' %(slot,ch)].is_set())&(get_channel_status(slot,ch)==0):
                lzamp.set_channel_enable(slot,ch,1)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass

#def loop_board_disable(slot):
#    try:
#        while (not end_log.is_set()):
#            sleep(1)
#            board_lock.acquire()
#            if globals()['board_%s_disable' %(slot)].is_set():
#                set_board_enable(slot,0)
#            elif (not globals()['board_%s_disable' %(slot)].is_set())&(get_board_status==0):
#                set_board_enable(slot,1)
#            board_lock.release()
#            
#    except:
#        error.set()
#        print('ERROR: failure with enabling/disabling board') 

def board_disabler(slot):
    try:
        if globals()['board_%s_disable' %(slot)].is_set()&(get_board_status==1):
            set_board_enable(slot,0)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass
        
def board_enabler(slot):
    try:
        if (not globals()['board_%s_disable' %(slot)].is_set())&(get_board_status==0):
            set_board_enable(slot,1)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass
    

#def loop_crate_disable():
#    try:
#        while (not end_log.is_set()):
#            sleep(1)
#            crate_lock.acquire()
#            if (crate_disable.is_set())&(power.is_set()):
#                lzamp.power_off()
#                power.clear()
#            elif (not crate_disable.is_set())&(not power.is_set()):
#                lzamp.power_on()
#                power.set()
#            crate_lock.release()
#            
#    except:
#        error.set()
#        print('ERROR: failure with enabling/disabling crate') 
        
def crate_disabler():
    try:
        if (crate_disable.is_set())&(power.is_set()):
            lzamp.power_off()
            power.clear()
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass

def crate_enabler():
    try:
        if (not crate_disable.is_set())&(not power.is_set()):
             lzamp.power_on()
             power.set()
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass
                
def loop_get_date():
    try:
        global c_date
        while (not end_log.is_set()):
            c_date=date.today().strftime("%d_%m_%Y")
            sleep(10)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass

def loop_data_logging(serNums):
    global c_pos_voltage, c_neg_voltage, c_pos_current, c_neg_current, c_air_flow, c_af_temp, c_SC_temp
    
    global c_AMP_temps
    c_AMP_temps=zeros((4,4))
    
    global c_DC_offsets
    c_DC_offsets=zeros((4,8))
    
    log_dir='/home/debian/LZAMP/daily_logs/'
    try:
        write_str='{:.4g}, '
        while (not end_log.is_set()): 
            sleep(20)
            
            fname='data_{:d}_{:d}_{:d}_{:d}_'+c_date+'.csv'
            fname=fname.format(*serNums)
            if not isfile(log_dir+fname):
                print('\ncreating data log file\n')
                with open(log_dir+fname,'w+') as f:
                    f.write("time (s), air flow (mm/s), af temp, SC temp, B1T1, B1T2, B1T3, "+
                            "B1T4, B2T1, B2T2, B2T3, B2T4, B3T1, B3T2, B3T3, B3T4, B4T1, B4T2, B4T3, B4T4, "+
                            "B1DC1, B1DC2, B1DC3, B1DC4, B1DC5, B1DC6, B1DC7, B1DC8, "+
                            "B2DC1, B2DC2, B2DC3, B2DC4, B2DC5, B2DC6, B2DC7, B2DC8, "+
                            "B3DC1, B3DC2, B3DC3, B3DC4, B3DC5, B3DC6, B3DC7, B3DC8, "+
                            "B4DC1, B4DC2, B4DC3, B4DC4, B4DC5, B4DC6, B4DC7, B4DC8, "+
                            "I+ (A), I- (A), V+, V-, NumChEnabled,\n")
                    print('\ndata currently logging to: '+log_dir+fname+'\n')
            
            with open(log_dir+fname,'a+') as f:
                
                c_time=localtime()
                seconds_since_midnight = int(c_time.tm_hour*3600+c_time.tm_min*60+c_time.tm_sec)
                f.write(write_str.format(seconds_since_midnight))
                sleep(0.1)
                
                
                c_air_flow=lzamp.get_airflow()
                c_af_temp=lzamp.get_airflow_temp()
                f.write(write_str.format(c_air_flow))
                f.write(write_str.format(c_af_temp ))
                sleep(0.1)
                
                c_SC_temp=lzamp.get_temp()
                f.write(write_str.format(c_SC_temp))
                sleep(0.1)
                
                for ii in range(4):
                    for jj in range(4):
                        c_AMP_temps[ii][jj]=lzamp.get_AMP_temp(ii+1,jj+1)
                        f.write(write_str.format(c_AMP_temps[ii][jj]))
                sleep(0.1)
                
                for ii in range(4):
                    for jj in range(8):
                        c_DC_offsets[ii][jj]=lzamp.get_channel_offset(ii+1,jj+1)
                        f.write(write_str.format(c_DC_offsets[ii][jj]))
                sleep(0.1)  
                
                c_pos_current=lzamp.get_current_pos()
                c_neg_current=lzamp.get_current_neg()
                f.write(write_str.format(c_pos_current))
                f.write(write_str.format(c_neg_current))
                sleep(0.1)
                
                c_pos_voltage=lzamp.get_voltage_pos()
                c_neg_voltage=lzamp.get_voltage_neg()
                f.write(write_str.format(c_pos_voltage))
                f.write(write_str.format(c_neg_voltage))
                sleep(0.1)
                
                f.write(write_str.format(c_channels_enabled))
                
                f.write('\n')
            
        print('\ndata logging ended\n')
        
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass

def loop_error_checking(**kwargs):
    global c_channels_enabled, c_thresh_current_low
    try:
        nn=0
        mm=zeros((4,8))
        while (not end_log.is_set()):
            sleep(30)
        
            crate_lock.acquire()
            if (c_air_flow<air_flow_min):
                nn+=1
                airflow_log.info('Low airflow detected')
            elif (c_air_flow>air_flow_min):
                nn=0
            if (nn>=5)&(not crate_disable.is_set()):
                airflow_log.error('Continuous low airflow detected...Shutting off crate...')
                crate_disable.set()
                crate_disabler()
            crate_lock.release()
            sleep(0.01)
            
            crate_lock.acquire()
            if (c_SC_temp>high_thresh_SC_temp)&(not crate_disable.is_set()):
                SC_temp_log.critical('SC board temperature exceeded %sC...Shutting off crate...'%(high_thresh_SC_temp))
                crate_disable.set()
                crate_disabler()
            elif (c_SC_temp>mid_thresh_SC_temp)&(c_SC_temp<high_thresh_SC_temp):
                SC_temp_log.error('SC board temperature exceeded %sC'%(mid_thresh_SC_temp))
            elif (c_SC_temp>low_thresh_SC_temp)&(c_SC_temp<mid_thresh_SC_temp):
                SC_temp_log.warning('SC board temperature exceeded %sC'%(low_thresh_SC_temp))
            crate_lock.release()
            sleep(0.01)
            
            board_lock.acquire()
            for ii in range(4):
                for jj in range(4):
                    if c_AMP_temps[ii][jj]>high_thresh_AMP_temp:
                        if (get_board_status(ii+1)==1)&(not globals()['board_%s_disable' %(ii+1)].is_set()):
                            AMP_temp_log.critical('AMP board %s temp exceeded %sC...Shutting down AMP...' %(ii+1,high_thresh_AMP_temp))
                            globals()['board_%s_disable' %(ii+1)].set()
                            board_disabler(ii+1)
                    elif (c_AMP_temps[ii][jj]>mid_thresh_AMP_temp)&(c_AMP_temps[ii][jj]<high_thresh_AMP_temp):
                        AMP_temp_log.error('AMP board %s temp exceeded %sC' %(ii+1,mid_thresh_AMP_temp))
                    elif (c_AMP_temps[ii][jj]>low_thresh_AMP_temp)&(c_AMP_temps[ii][jj]<mid_thresh_AMP_temp):
                        AMP_temp_log.warning('AMP board %s temp exceeded %sC' %(ii+1,low_thresh_AMP_temp))
            board_lock.release()
            sleep(0.01)
            
            channel_lock.acquire()
            for ii in range(4):
                sleep(1)
                for jj in range(8):
                    if absolute(c_DC_offsets[ii][jj])>min_thresh_DC_offset:
                        mm[ii][jj]+=1
                        DC_offset_log.warning('AMP board %s channel %s DC offset exceeded %smV'%(ii+1,jj+1,min_thresh_DC_offset))
                    elif absolute(c_DC_offsets[ii][jj])<min_thresh_DC_offset:
                        mm[ii][jj]=0
                    if (mm[ii][jj]>=5)&(get_channel_status(ii+1,jj+1)==1)&(not globals()['board_%s_ch_%s_disable' %(ii+1,jj+1)].is_set()):
                            DC_offset_log.critical('AMP board %s channel %s DC offset remained above %smV...Shutting down channel...'%(ii+1,jj+1,min_thresh_DC_offset))
                            globals()['board_%s_ch_%s_disable' %(ii+1,jj+1)].set()
                            channel_disabler(ii+1,jj+1)
                    if (absolute(c_DC_offsets[ii][jj])>high_thresh_DC_offset)&(get_channel_status(ii+1,jj+1)==1)&(not globals()['board_%s_ch_%s_disable' %(ii+1,jj+1)].is_set()):
                        DC_offset_log.critical('AMP board %s channel %s DC offset went above %smV...Shutting down channel...'%(ii+1,jj+1,high_thresh_DC_offset))
                        globals()['board_%s_ch_%s_disable' %(ii+1,jj+1)].set()
                        channel_disabler(ii+1,jj+1)
            channel_lock.release()
            sleep(0.01)
            
            crate_lock.acquire()
            if (c_pos_current > min_thresh_current_high )&(not crate_disable.is_set()):
                current_log.error('+ Current: %s, out of expected range' %c_pos_current)
                if (c_pos_current >high_thresh_current_high)&(not crate_disable.is_set()):
                    current_log.critical('+ Current: %s, is too high...Shutting down crate...' %c_pos_current)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)
            
            if (c_neg_current > min_thresh_current_high )&(not crate_disable.is_set()):
                current_log.error('- Current: %s, out of expected range' %c_neg_current)
                if (c_neg_current >high_thresh_current_high)&(not crate_disable.is_set()):
                    current_log.critical('- Current: %s, is too high...Shutting down crate...' %c_neg_current)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)
            
            
            c_channels_enabled=get_channel_enabled_count()
            c_thresh_current_low=0.07*c_channels_enabled
            
            if (c_neg_current < c_thresh_current_low )&(not crate_disable.is_set()):
                if c_channels_enabled>=8:
                    current_log.critical('- Current: %s, lower than expected...Shutting down crate...' %c_neg_current)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)
                else:
                    current_log.error('- Current: %s, lower than expected' %c_neg_current)
            
            if (c_pos_current < c_thresh_current_low )&(not crate_disable.is_set()):
                if c_channels_enabled>=8:
                    current_log.critical('+ Current: %s, lower than expected...Shutting down crate...' %c_pos_current)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)
                else:
                    current_log.error('+ Current: %s, lower than expected' %c_pos_current)

            crate_lock.release()
            
            sleep(0.01)
            
            crate_lock.acquire()
            
            if (c_pos_voltage > min_thresh_volt_high )&(not crate_disable.is_set()):
                voltage_log.error('+ Voltage: %s, out of expected range' %c_pos_voltage)
                if (c_pos_voltage >high_thresh_volt_high)&(not crate_disable.is_set()):
                    voltage_log.critical('+ Voltage: %s, is too high...Shutting down crate...' %c_pos_voltage)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)
            
            if (c_pos_voltage < high_thresh_volt_low )&(not crate_disable.is_set()):
                voltage_log.error('+ Voltage: %s, out of expected range' %c_pos_voltage)
                if (c_pos_voltage < min_thresh_volt_low)&(not crate_disable.is_set()):
                    voltage_log.critical('+ Voltage: %s, is too low...Shutting down crate...' %c_pos_voltage)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)
            
            if (c_neg_voltage > min_thresh_volt_high )&(not crate_disable.is_set()):
                voltage_log.error('- Voltage: %s, out of expected range' %c_neg_voltage)
                if (c_neg_voltage >high_thresh_volt_high)&(not crate_disable.is_set()):
                    voltage_log.critical('- Voltage: %s, is too high...Shutting down crate...' %c_neg_voltage)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)

            if (c_neg_voltage < high_thresh_volt_low )&(not crate_disable.is_set()):
                voltage_log.error('- Voltage: %s, out of expected range' %c_neg_voltage)
                if (c_neg_voltage < min_thresh_volt_low)&(not crate_disable.is_set()):
                    voltage_log.critical('- Voltage: %s, is too low...Shutting down crate...' %c_neg_voltage)
                    crate_disable.set()
                    crate_disabler()
                    sleep(0.1)

            crate_lock.release()

    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        exception_traceback_log.exception('The following error occurred:')
        pass

if __name__ == '__main__':
    
#    logging.basicConfig(filename='monitor.log', filemode='a', level=logging.DEBUG, format=LOG_FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')

    formatter=logging.Formatter('%(levelname)s %(asctime)s %(name)s: %(message)s','%m/%d/%Y %I:%M:%S %p')
    
    SC_temp_log=setup_logger('SC_temp','error_handling_monitor.log')
    airflow_log=setup_logger('airflow','error_handling_monitor.log')
    AMP_temp_log=setup_logger('AMP_temp','error_handling_monitor.log')
    current_log=setup_logger('current','error_handling_monitor.log')
    voltage_log=setup_logger('voltage','error_handling_monitor.log')
    DC_offset_log=setup_logger('DC_offset','error_handling_monitor.log')
    exception_traceback_log=setup_logger('Exception Traceback','exception_handling_monitor.log')
    
    for ii in range(4):
        globals()['board_%s_disable' %str(ii+1)]=Event()
        for jj in range(8):
            globals()['board_%s_ch_%s_disable' %(ii+1,jj+1)]=Event()
        
    crate_disable=Event()
    power=Event()
    end_log=Event()
    error=Event()
    
    crate_lock=Lock()
    channel_lock=Lock()
    board_lock=Lock()
    
    lzamp.setup()
    lzamp.power_off()
    lzamp.test_on()
    
    serNums=[0,0,0,0]
    for slot in range(1,5):
        tmp=lzamp.get_serNum(slot)
        serNums[slot-1]=tmp
   
    air_flow_min=300
    
    low_thresh_SC_temp=30
    mid_thresh_SC_temp=35
    high_thresh_SC_temp=40
    
    low_thresh_AMP_temp=40
    mid_thresh_AMP_temp=45
    high_thresh_AMP_temp=50
    
    min_thresh_DC_offset=1
    high_thresh_DC_offset=10
    
    min_thresh_volt_high=9
    high_thresh_volt_high=10
    min_thresh_volt_low=5
    high_thresh_volt_low=6
    
    min_thresh_current_high=3.1
    high_thresh_current_high=3.2
    
    c_channels_enabled=-1

    lzamp.power_on()
    power.set()
    
    threads=[]
    threads.append(Thread(target=loop_get_date))
    threads.append(Thread(target=loop_heartbeat))
    threads.append(Thread(target=loop_data_logging,args=(serNums,)))
    print('\nBeginning Data Logging\n')
    threads.append(Thread(target=loop_error_checking))
    print('\nBeginning Error Checking\n')
    
    for t in threads:
        t.start()  
        sleep(.05)
        
    ii=0
    jj=1
    while (not end_log.is_set()):
        try:
            ii+=1
            if ii==21:
                ii=0
                jj*=-1
            elif jj>0:
                print('\b'*20+'+'*20,end='')
            else:
                print('\b'*20+'-'*20,end='')
            sys.stdout.flush()
            sleep(.05)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            exception_traceback_log.exception('The following error occurred:')
            pass

    print('\nData Logging Stopping...\n')
    
    for t in threads:
        t.join()
            
    lzamp.power_off()
    lzamp.test_off()
    
    if (end_log.is_set()):
        print('\nData Logging Ended...\n')