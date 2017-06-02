# -*- coding:utf-8 -*-
import datetime
import time
import ntplib
import os
import platform
import traceback
import threading
ADJUST_THRESHOLD = 0.001
INTERVAL = 3

class ntpThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server_ip = '127.0.0.1'
        self.client = ntplib.NTPClient()
        self.offset_count = 0
        self.delta = 0.04 #diff time due to program process
        self.interval = INTERVAL
        self.status = ''
        self.is_run = False

    def stop(self):
        self.is_run = False

    def run(self):
        self.is_run = True
        while self.is_run:
            try:
                response = self.client.request(self.server_ip)
            except Exception, e:
                traceback.print_exc()
                self.status = str(e)
                continue 
            ts = response.tx_time  
            if self.offset_count == 0:
                self.offset_count = response.offset
            else:
                self.offset_count = self.offset_count * 0.6 + 0.4 * response.offset
            self.status = str(response.offset)
            #print 'offset=', response.offset,'  ',
            #print 'offset_count=',self.offset_count,
            #print 'delta=',self.delta
            if abs(self.offset_count) > ADJUST_THRESHOLD:
                if abs(self.offset_count) < 0.1:
                    self.delta = self.delta + self.offset_count * 0.9
                ts = ts + self.delta
                _date = time.strftime('%Y-%m-%d',time.localtime(ts+1)) 
                _time = time.strftime('%X',time.localtime(ts+1)) 
                ms = int(ts+1) - ts
                self.offset_count = 0
                #print '---------------------'
                #Set the time at the next integer second
                time.sleep(ms)
                if platform.system() == "Windows":
                    os.system('date {} && time {}'.format(_date,_time))
                if platform.system() == "Linux":
                    date_string =  _date + ' ' + _time
                    os.system('date -s "{}" '.format(date_string ))
            time.sleep(self.interval)
      
      
    def set_ntp_server(self, server_ip):
        self.server_ip = server_ip

    def set_update_interval(self, s): #unit:second
        self.interval = s            

    def get_ntp_status(self):
        return self.status  

    def set_ntp_status(self, s):
        self.status = s 

if __name__ == "__main__":
    iv = 3
    thread1 = ntpThread()
    thread1.set_ntp_server('202.120.39.169')
    thread1.set_update_interval(iv)
    thread1.setDaemon(True)
    thread1.start()
    while True:
        time.sleep(iv)
        print thread1.get_ntp_status()
        
