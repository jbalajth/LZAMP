import LZAMP_CTRL as lzamp
from time import sleep, time
from threading import Thread, Event
import sys

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


def loop_AMP_heartbeat():
    try:
        print('amp heartbeat started')
    
        while (not event.is_set()):
            lzamp.set_AMP_alert_on(1)
            sleep(0.1)
            lzamp.set_AMP_alert_on(2)
            sleep(0.1)
            lzamp.set_AMP_alert_on(3)
            sleep(0.1)
            lzamp.set_AMP_alert_on(4)
            sleep(0.1)
            lzamp.set_AMP_alert_off(1)
            sleep(0.1)
            lzamp.set_AMP_alert_off(2)
            sleep(0.1)
            lzamp.set_AMP_alert_off(3)
            sleep(0.1)
            lzamp.set_AMP_alert_off(4)
            sleep(0.5)
            
        print('amp heartbeat stopped')
    except:
        error.set()
        print('ERROR: amp heartbeat failure')


def loop_get_data(t0,serNums,tester,date,tstart):
    try:
        fname='data_{:d}_{:d}_{:d}_{:d}.csv'.format(*serNums)
        print('data logging started under file name: '+fname)
        with open(fname,'w+') as f:
            f.write(("Burn in test for boards {:d}, {:d}, {:d}, {:d}. Tested by "+tester+" beginning on "+date+
                    " at "+tstart+"\n\n").format(*serNums))
            f.write("PASSED power cycle test\nPASSED channel enable/disable test.\n")
            for slot in range(1,5):
                for ch in range(1,9):
                    tmp=lzamp.get_channel_offset(slot,ch)**2
                    if tmp>1:
                        print('ERROR: bad offset')
                        error.set()
            f.write("PASSED pre-burn in offset test test\n")
                        
    
            f.write("time (s), air flow (mm/s), af temp, SC temp, B1T1, B1T2, B1T3, "+
                    "B1T4, B2T1, B2T2, B2T3, B2T4, B3T1, B3T2, B3T3, B3T4, B4T1, B4T2, B4T3, B4T4, I+ (A), I- (A), V+, V-,\n") 
        
        write_str='{:.4g}, '
        nn=0
        while ((time()-t0)<(3600*24))&(not event.is_set()):
            with open(fname,'a+') as f:
                f.write(write_str.format(time()-t0))
                af=lzamp.get_airflow() 
                if (af<300):
                    nn+=1
                else:
                    nn=0
                if nn>5:
                    error.set()
                    print('Low Airflow')
                    
                f.write(write_str.format(af))
                
                f.write(write_str.format(lzamp.get_airflow_temp() ))
                
                t=lzamp.get_temp()
                if t>40:
                    error.set()
                    print('SC Overheated')
                    
                f.write(write_str.format(t))
                for ii in range(4):
                    for jj in range(4):
                        t=lzamp.get_AMP_temp(ii+1,jj+1)
                        if t>50:
                            error.set()
                            print('AMP Overheated')
                        f.write(write_str.format(t))
                
                val=lzamp.get_current_pos()
                if (val < 2.0)|(val > 3.0 ):
                    error.set()
                    print("+ Current out of range")
                f.write(write_str.format(val))
                
                val=lzamp.get_current_neg()
                if (val < 2.0)|(val > 3.0 ):
                    error.set()
                    print("- Current out of range")
                f.write(write_str.format(val))
                
                val=lzamp.get_voltage_pos()
                if (val < 6)|(val > 10 ):
                    error.set()
                    print("+ Voltage out of range")
                f.write(write_str.format(val))
                
                val=lzamp.get_voltage_neg()
                if (val < 6)|(val > 10 ):
                    error.set()
                    print("- Voltage out of range")
                f.write(write_str.format(val))
                
                f.write('\n')
                
            if error.is_set():
                break
            sleep(60)
            
        for slot in range(1,5):
            for ch in range(1,9):
                tmp=lzamp.get_channel_offset(slot,ch)**2
                if tmp>1:
                    print('ERROR: bad offset')
                    error.set()
        with open(fname,'r') as f:
            contents = f.readlines()
        contents.insert(5,"PASSED Burn in test\n\n")
        contents.insert(5,"PASSED post-burn in offset test test\n")
        contents = "".join(contents)
        with open(fname,'w') as f:
            f.write(contents)   
            
        complete.set()
        
        print('\ndata logging stopped')
    except:
        print('data logging failed')
        error.set()
    
    
def insert_board(slot_num):
    try:
        pos=lzamp.switch_pos(slot_num)
        serNum=input(("Insert Board in slot # {:d}, with swith in position "+ pos+
        "\nOnce inserted, enter serial number: ").format(slot_num))
        tmp=lzamp.set_serNum(slot_num,serNum)
        sleep(1)
        tmp=lzamp.get_serNum(slot_num)  
        if tmp == serNum:
            return(serNum)
        else:
            return(-1)
    except:
        return(-2)
    

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
    
    # tester='JB'
    # date='12/15/2019'
    # tstart='0000'
    # serNums=[605,608,607,606]
    
    tester=raw_input('Enter name of tester: ')
    date=raw_input('Enter date: (MM/DD/YYYY) ')
    tstart=raw_input('Enter start time in 24-hour format: (1:17 pm would be 1317) ')
    
    serNums=[0,0,0,0]
    for slot in range(1,5):
        ii=0
        while (ii<5):
            snum=insert_board(slot)
            ii+=1
            if snum>=0:
                print('\nSerial Number {:d} successfully written to board.\n'.format(snum))
                serNums[slot-1]=snum
                break
            elif ii<5:
                print('\nUnable to write serial number to board, try again.\n')
            else:
                print('\nFatal error occurred, exiting\n')
                exit()
    
    
    if check_input_yn('\nAre green lights off on all amp boards? (y/n) '):   
        print('fatal error, exiting.')
        exit()
        
    lzamp.power_on()
    
    if check_input_yn('\nAre green lights now lit on all amp boards? (y/n) '):   
        print('fatal error, exiting.')
        exit()
         
        
    t=Thread(target=loop_AMP_heartbeat)
    t.start()
    sleep(1)
    
    if check_input_yn('\nAre the red LEDs on the AMPs flashing in the correct order (1, 2, 3, 4)? (y/n) '): 
        print('fatal error, exiting. AMPs were installed incorrectly.')
        event.set()
        t.join()
        exit()
            
    event.set()
    t.join()
    event.clear()
    
    
        
    print('\n\nTesting digital switch functionality\n')
    for slot in range(1,5):
        for ch in range(1,9):
            lzamp.set_channel_enable(slot,ch,1)
    t=Thread(target=loop_test)
    t.start()
    sleep(1)
    
    if check_input_yn(('Use scope to probe channels 1 and 2 HG on all slots.'+
                       'Is test pulse visible on all channels? (y/n) ')):
        print('fatal error, exiting.')
        event.set()
        t.join()
        exit()
            
            
    for slot in range(1,5):
        lzamp.set_channel_enable(slot,2,0)
    if check_input_yn(('\nCheck same channels again. '+
                '\nIs test pulse visible on channel 1, but not 2 for all slots? (y/n) ')):
        print('fatal error, exiting.')
        event.set()
        t.join()
        exit()
    
    lzamp.power_off()
    sleep(1)
    tmp=raw_input('Remove and reinsert all AMP boards, then press enter.\n')
    
    print("Checking serial nums")
    for slot in range(1,5):
        tmp=lzamp.get_serNum(slot)
        if not (tmp==serNums[slot-1]):
            print('fatal error, serial numbers not perserved, exiting.')
            event.set()
            t.join()
            exit()
    print('good\n')

    print("Checking current")
    if (lzamp.get_current_neg()>1)|(lzamp.get_current_pos()>1):
        print('fatal error, power not off. exiting.')
        event.set()
        t.join()
        exit()
    print('good\n')
    
    lzamp.power_on()
    print("Checking current")
    if (abs(lzamp.get_current_neg()-2.5)>0.6)|(abs(lzamp.get_current_pos()-2.5)>0.6):
        print('fatal error, power not on. exiting.')
        event.set()
        t.join()
        exit()
    print('good\n')

    if check_input_yn(('\nProbe same channels again with scope. '+
            '\nIs test pulse visible on channel 1, but not 2 for all slots? (y/n) ')):
        print('fatal error, exiting.')
        event.set()
        t.join()
        exit()
    
    for slot in range(1,5):
        lzamp.set_channel_enable(slot,2,1)
        
    if check_input_yn(('\nCheck same channels one more time.'+
            '\nIs test pulse visible on all channels for all slots? (y/n) ')):
        print('fatal error, exiting.')
        event.set()
        t.join()
        exit()
    
    event.set()
    t.join()
    event.clear()
    
    print('\n\n\nBeginning burn-in test\n\n')
    t0=time()
    
    lzamp.power_on()
    
    threads=[]
    threads.append(Thread(target=loop_heartbeat))
    threads.append(Thread(target=loop_AMP_heartbeat))
    threads.append(Thread(target=loop_test))
    threads.append(Thread(target=loop_get_data,args=(t0,serNums,tester,date,tstart)))

    for t in threads:
        t.start()  
        sleep(1)
        

    ii=0
    jj=1
    while (not error.is_set())&(not complete.is_set()):
        try:
            ii+=1
            if ii==21:
                print('\b'*ii),
                ii=0
                jj*=-1
            elif jj>0:
                print('\b.'),
            else:
                print('\b '),
            sys.stdout.flush()
            sleep(1)
        except KeyboardInterrupt:
            error.set()
            break
    print('\nStopping...')
    event.set()

    for t in threads:
        t.join()

    
    lzamp.power_off()
    lzamp.test_off()
    lzamp.set_AMP_alert_off(1)
    lzamp.set_AMP_alert_off(2)
    lzamp.set_AMP_alert_off(3)
    lzamp.set_AMP_alert_off(4)
    
    if (error.is_set()):
        print('\nTerminated on error condition')
    elif (complete.is_set()):
        print('Burn-in Test Completed Successfully')
    
    
    
