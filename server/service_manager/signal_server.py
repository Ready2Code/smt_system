#!/usr/bin/env python
# Minghao LI 2017-2-20
import json
import time
import socket 
import sys
import urllib2
import shlex
import os
import shutil
import platform
import signal
from datetime import datetime, timedelta
from threading import Timer, Thread, Event
from subprocess import call,Popen,PIPE,STDOUT
from itertools import cycle
from utils import functions
import urllib, urlparse

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('20110101','%Y%m%d')

FNULL = open(os.devnull, 'w')

LOCAL_PORT = 8001
FILE_RELATIVE_PATH = './'
if platform.system() == "Windows":
    SETTING_RELATIVE_PATH = '..\\related\\'
elif platform.system() == "Linux":
    SETTING_RELATIVE_PATH = '../related/'

CHANNEL_FILE_NAME = SETTING_RELATIVE_PATH + 'channels.json'
CONFIG_FILE_NAME =  SETTING_RELATIVE_PATH + 'programs.json'
POSTER_PATH = 'resources/static/'
DESTINATION_IP = '127.0.0.1'
#DESTINATION_IP = '192.168.1.212'

BROADCASE_TIME_INTERVAL = 0.5   #seconds

RESERVED_POS_ONE = 1
RESERVED_POS_TWO = 0
CHANNEL_NUM = 1
BROADBAND_SERVER_IP = '127.0.0.1'
#BROADCAST_SERVER_IP = '239.1.1.1'
BROADCAST_SERVER_IP = '127.0.0.1'
AVLOGEXT_IP = '127.0.0.1'
AVLOGEXT_PORT = 7778

class PlayOrderType:
    (singleloop, loop, onebyone, unknown) = range(0,4)

    @staticmethod
    def getType(s):
        if(s == 'singleloop'):
            return PlayOrderType.singleloop
        elif(s == 'loop'):
            return PlayOrderType.loop        
        elif(s == 'onebyone'):
            return PlayOrderType.onebyone  
        else:
            return PlayOrderType.unknown
            
play_order_type = PlayOrderType.onebyone
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
packet = ''
endtime = datetime.now()
aheadtime = 3000
cachetime = 5000
sequence_number = 0
program_num = 1
resource_num = 1
destination = DESTINATION_IP
programmers  = {}
#################thread flag######################
signal_timer_thread_flag=1
start_system_flag=1
ffmpeg_list=list()
ext_callbacks ={}
signal_destination = ('127.0.0.1',9999)

class SignalTimerThread(Thread):
    def __init__(self, event, dest):
        Thread.__init__(self)
        self.stopped = event
        self.dests = [dest]
        self.program_url = ''

    def add_dest(self, dest):
        self.dests.append(dest)
        
    def update_url(self,file):
        self.program_url = file

    def run(self):
        global signal_timer_thread_flag
        global ext_callbacks

        if ext_callbacks.has_key('before_ffmpeg'):
            ext_callbacks['before_ffmpeg']('broadcast', self.dests[0][0]+':'+str(self.dests[0][1]))

        while not self.stopped.wait(BROADCASE_TIME_INTERVAL):
            if signal_timer_thread_flag==1:
                if self.program_url != '':
                    update_signal(self.program_url, BROADCAST_SERVER_IP, BROADBAND_SERVER_IP)
                for dest in self.dests:
                    delay_broadcast(s, packet, dest)
            else:
                break

        if ext_callbacks.has_key('after_ffmpeg'):
            ext_callbacks['after_ffmpeg']('broadcast', self.dests[0][0]+':'+str(self.dests[0][1]))
            #ext_callbacks['after_ffmpeg'](res_type, str_output)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def load(name):
    if not name.startswith('/') and not name.startswith('.'):  name = SETTING_RELATIVE_PATH + name
    with open(name) as json_file:
        data = json.load(json_file)
        return data

def url_load(url):
    data = urllib2.urlopen(url)
    return data.read()

def cal_delta_time(tt):
    t = datetime.strptime(tt,'d%H:%M:%S')
    delta = timedelta(hours=t.hour,minutes=t.minute,seconds=t.second)
    delta += timedelta(milliseconds=(aheadtime+cachetime))
    return delta

def update_delta_time(tt, now):
    deltatime = cal_delta_time(tt)
    tt = deltatime + now
    return tt 

def first_signal(dest):
    string  = '{"programmer": {"sequence": 0}}'
    counter = 300

    if ext_callbacks.has_key('before_ffmpeg'):
        ext_callbacks['before_ffmpeg']('broadcast', dest[0]+':'+str(dest[1]))
    while counter > 0:
        s.sendto(string, dest)
        counter = counter - 1
        time.sleep(0.01)
    
def convert_signal(json_data, resource_broadcast_ip, resource_broadband_ip,avlogext='',static_resource_host='', dir_name='/'):
#def convert_signal(json_file, resource_broadcast_ip, resource_broadband_ip,static_resource_host,avlogext=''):
    global resource_num
    global sequence_number
    global packet
    global ffmpeg_list
    global play_order_type 
    
#    for i in range(len(ffmpeg_list)):
#        functions.kill_process_by_name(ffmpeg_list[i]["cmd"])
#    del ffmpeg_list[:]

    #json_data = json.loads(json_file)
    sequence_number += json_data['programmer']['sequence']
    json_data['programmer']['sequence'] = sequence_number
    json_data['programmer']['begin'] = update_delta_time(json_data['programmer']['begin'], endtime)
    json_data['programmer']['end'] = update_delta_time(json_data['programmer']['end'], endtime)

    resources = json_data['programmer']['resources']
    for res in resources:
        localfile = ''
        bkfile = ''
        ffplaybk_port = ''
        ffmpegbk_port = ''
        if play_order_type == PlayOrderType.singleloop:
            res['end'] = "d23:59:59"
        if 'url' in res.keys(): localfile = res['url']
        elif ('playlist' in res.keys()): localfile = res['playlist']
        if ('bk' in res.keys()): 
            bkfile = res['bk']
            if not os.path.isabs(bkfile):
                bkfile = os.path.normpath(dir_name+'/'+bkfile)
            #if bkfile.encode('ascii', 'ignore').startswith('./'):
            #    bkfile = bkfile.replace('./', FILE_RELATIVE_PATH)  
        if(localfile == ''): print 'error url or playlist has to been assigned' 
        localfile = localfile.replace('?' , '-' + res['type'] )
        if not os.path.isabs(localfile):
            localfile = os.path.normpath(dir_name+'/'+localfile)
        #if localfile.encode('ascii', 'ignore').startswith('./'):
        #    localfile = localfile.replace('./', FILE_RELATIVE_PATH)
        ffplay_port = '{0}{1}{2}{3}{4}'.format(RESERVED_POS_ONE,RESERVED_POS_TWO, CHANNEL_NUM, program_num, resource_num)
        ffmpeg_port = '{0}{1}{2}{3}{4}'.format(RESERVED_POS_ONE, 1, CHANNEL_NUM, program_num, resource_num)
        if(res['type'] == 'broadcast'):
            res['url'] = 'smt://{0}:{1}'.format(resource_broadcast_ip, ffplay_port)
            if ('bk' in res.keys()):
                ffplaybk_port = '{0}{1}{2}{3}{4}'.format(RESERVED_POS_ONE,2, CHANNEL_NUM, program_num, resource_num)
                ffmpegbk_port = '{0}{1}{2}{3}{4}'.format(RESERVED_POS_ONE, 3, CHANNEL_NUM, program_num, resource_num)
                res['bk']='smt://{0}:{1}@:{2}'.format(resource_broadband_ip, ffmpegbk_port,ffplaybk_port)
        elif(res['type'] == 'broadband'):
            res['url'] = 'smt://{0}:{1}@:{2}'.format(resource_broadband_ip, ffmpeg_port,ffplay_port)
        else:
            print 'error unknown type in resources'

        res['begin'] = update_delta_time(res['begin'], endtime)
        res['end'] = update_delta_time(res['end'], endtime)

        if 'poster' in res.keys():
            if not os.path.isabs(res['poster']):
                res['poster'] = os.path.normpath(dir_name+'/' + res['poster'])
            (path, name) = os.path.split(res['poster'])
            shutil.copy(res['poster'], POSTER_PATH + name)
            res['poster'] = 'http://' + static_resource_host + '/static/' + name
            
        #print str(res['begin'])

        t = Thread(target=call_ffmpeg, args=(localfile, res, ffmpeg_port, resource_broadcast_ip, ffplay_port, avlogext))
        t.daemon = True
        t.start()
        resource_num += 1
        resource_num = resource_num % 10
        time.sleep(0.1)

        if ('bk' in res.keys()):
            res_bk = res.copy()
            res_bk["type"] = "broadband"
            res_bk["begin"] = res["begin"] 
            res_bk["end"] = res["end"] 
            if('playlist' in res.keys()): res_bk["playlist"] = res["playlist"] 
            time.sleep(2.5)
            t = Thread(target=call_ffmpeg, args=(bkfile, res_bk, ffmpegbk_port, '', ffplaybk_port, avlogext))
            t.daemon = True
            t.start()
            time.sleep(0.1)
    return json_data

def get_begin_time_string(begin_time, zone_offset='default'):
    if 'default' == zone_offset:
        now_stamp = time.time()
        local_time = datetime.fromtimestamp(now_stamp)
        utc_time = datetime.utcfromtimestamp(now_stamp)
        zone_offset = local_time - utc_time
    begin_time_with_zone_offset = begin_time + zone_offset
    begin_time_utc_string = begin_time_with_zone_offset.strftime("%Y-%m-%dT%H:%M:%S.%f")
    return begin_time_utc_string
    
def call_ffmpeg(file_dir, res, port, resource_broadcast_ip, ffplay_port, avlogext=''):
    global play_order_type
    time.sleep(aheadtime/1000)
    begintime = get_begin_time_string(res['begin'],timedelta(hours=8))
    res_type = res['type']
    delta = res['end'] - res['begin']
    ffmpeg_command = ''
    playlist = ''
    str_avlogext = ''
    str_output = ''
    str_port = ''
    if('playlist' in res.keys()): playlist = '-f concat'
    if platform.system() == "Windows":
        ffmpeg_command = SETTING_RELATIVE_PATH + 'ffmpeg.exe'
    if platform.system() == "Linux":
        ffmpeg_command = SETTING_RELATIVE_PATH + 'ffmpeg'

    if(len(avlogext) != 0):
        str_avlogext = '-avlogext ' + avlogext + ' -deviceinfo ' + res['id']

    if(res_type == 'broadband' or resource_broadcast_ip == ''):
        str_port ='-port %s' % port
        str_output = 'smt://%s:%s' % (BROADBAND_SERVER_IP, 1)
    elif(res_type == 'broadcast'):
        str_port ='-port %s' % port
        str_output = 'smt://%s:%s' % (resource_broadcast_ip, ffplay_port)
        
    str_duration = ''
    if play_order_type == PlayOrderType.singleloop:
        str_duration = ' -stream_loop -1'
    else:
        str_duration = ' -t %s' % delta

    #ffmpeg_command = ffmpeg_command + ' -re  {0} {1} -t {6} -i {2} -begintime {3} {4} -c:v copy -c:a aac -f mpu {5}'.format(str_port, playlist, file_dir, begintime, str_avlogext, str_output, delta) 
    ffmpeg_command = ffmpeg_command + ' -re ' + str_port + playlist \
                     + str_duration +' -i '+file_dir +' -begintime '+ begintime \
                     + ' ' +str_avlogext +' -c:v copy -c:a copy -f mpu '+str_output

    print ffmpeg_command

    ffmpeg_list.append({"cmd":ffmpeg_command, "end":res['end']})

    if ext_callbacks.has_key('before_ffmpeg'):
        ext_callbacks['before_ffmpeg'](res_type, str_output)

    try:
        os.system(ffmpeg_command)
    except:
        print "error ---------------------------------------" 

    if ext_callbacks.has_key('after_ffmpeg'):
        ext_callbacks['after_ffmpeg'](res_type, str_output)

def stop_all():
    global signal_timer_thread_flag
    global start_system_flag
    global stopFlag
    global packet
    global ffmpeg_list
    global sequence_number
    global signal_destination 

    signal_timer_thread_flag=0
    start_system_flag=0
    sequence_number = 0
    stopFlag.set()
    packet = ''

    print "stop all!!!!!!!!!!!!!!!!"
    print signal_timer_thread_flag
    print start_system_flag
    print range(len(ffmpeg_list))
    for i in range(len(ffmpeg_list)):
        #ffmpeg_list[i].kill()
        #ffmpeg_list[i].wait()
        functions.kill_process_by_name(ffmpeg_list[i]["cmd"])
    del ffmpeg_list[:]

no_signal_print_couter = 0
def delay_broadcast(s, packet, des):
    global no_signal_print_couter
    if len(packet) == 0:
        return

    cur = datetime.now()
    if ( cur > packet['programmer']['begin'] - timedelta(milliseconds=(aheadtime+cachetime)) and cur < packet['programmer']['end'] - timedelta(milliseconds=(aheadtime+cachetime))):
        #print 'Dest:',des,' Duration:', packet['programmer']['begin'], '~', packet['programmer']['end'],' Now:', datetime.now(), 'SIGNAL sending ', packet['programmer']['name']
        sp = json.dumps(packet, cls=DateTimeEncoder)#.encode('utf8')
        s.sendto(sp, des)
        #print sp
        no_signal_print_couter = 0
    else:
        if no_signal_print_couter >= 5:
            return
        no_signal_print_couter = no_signal_print_couter + 1
        print 'no proper signal to send...'
        #pass

def command_timer():
    global ffmpeg_list
    while start_system_flag != 0:
        for i in range(len(ffmpeg_list)-1, -1, -1):
            delta = ffmpeg_list[i]['end'] - datetime.now()
            #if delta.seconds < 0:
            if ffmpeg_list[i]['end'] < datetime.now():
                functions.kill_process_by_name(ffmpeg_list[i]['cmd'])
                ffmpeg_list.pop(i)
        time.sleep(0.1)

def main():
    if len(sys.argv) != 4 and len(sys.argv) != 1:
        print 'Usage: %s <port> <programs.json> <destination>' % sys.argv[0]
        print '       or leave the parameters empty'
        return
    global signal_timer_thread_flag
    global start_system_flag
    global program_num
    global resource_num
    global packet
    global endtime
    #global destination
    global aheadtime
    global cachetime
    signal(signal.SIGCHLD,signal.SIG_IGN)
    if len(sys.argv) == 4:
        port = int(sys.argv[1])
        config_file = sys.argv[2]
        destip = sys.argv[3]
    elif len(sys.argv) == 1:
        port = LOCAL_PORT
        config_file = CONFIG_FILE_NAME
        destip = DESTINATION_IP
    start_smt_system(config_file, destip, port)

def start_smt_system(programs_file=CONFIG_FILE_NAME, 
                     signal_destip=DESTINATION_IP, 
                     signal_port=LOCAL_PORT,
                     resource_broadcast_ip = BROADCAST_SERVER_IP ,
                     resource_broadband_ip = BROADBAND_SERVER_IP ,
                     avlogext_ip           = AVLOGEXT_IP,
                     avlogext_port         = AVLOGEXT_PORT,
                     static_resource_host  = '',
                     callbacks = {}):
    global program_num
    global resource_num
    global packet
    global endtime
    global destination
    global aheadtime
    global cachetime
    global programmers
    global stopFlag
    global signal_timer_thread_flag 
    global ext_callbacks
    global signal_destination 
    global start_system_flag
    global play_order_type

    signal_timer_thread_flag = 1
    start_system_flag=1


    ext_callbacks = callbacks 
    json_data = load(programs_file)
    print "load file <" , programs_file , "> successful \n"

    signal_destination = (signal_destip, int(signal_port))
    aheadtime = int(json_data['aheadtime'])
    cachetime = int(json_data['cachetime'])
    programmers = json_data['programmers']
    try:
        play_order_type = PlayOrderType.getType(json_data['play_order_type'])
    except:
        print 'no play_order_type in program.json'    
    print 'aheadtime =', aheadtime , 'cachetime =', cachetime,'start_system_flag=',start_system_flag

    first_signal(signal_destination)
    stopFlag = Event()
    thread = SignalTimerThread(stopFlag, signal_destination)
    thread.add_dest((avlogext_ip, avlogext_port))
    thread.setDaemon(True)
    thread.start()
    t = Thread(target=command_timer)
    t.daemon = True
    t.start()

    endtime = datetime.now()
    for i in cycle(programmers):
        if start_system_flag==0:
            break
        else:
            url = i['url']
            print "processing", i['name'], url
            program_data = url_load(url)
            json_data=json.loads(program_data)
            print json_data['programmer']
            try:
                aheadtime =int( json_data['programmer']['aheadtime'])
            except:
                print 'no aheadtime in program.json'
            try:
                cachetime =int( json_data['programmer']['cachetime'])
            except:
                print 'no cachetime in program.json'

            dir_name = os.path.dirname(functions.url2pathname(url))
            resource_num = 1
            
            if play_order_type == PlayOrderType.singleloop:
                json_data['programmer']['end'] = "d23:59:59"
            
            convert = convert_signal(json_data, resource_broadcast_ip, resource_broadband_ip, avlogext_ip+':'+str(avlogext_port),static_resource_host,dir_name)
            packet = convert

            thread.update_url(url)
            program_num += 1
            program_num = program_num % 10
            #print convert

            #if play_order_type is singleloop, set endtime to long time later

            endtime = convert['programmer']['end'] - timedelta(milliseconds=(aheadtime+cachetime))


            while (endtime - datetime.now()).seconds > 0.05:
                if start_system_flag==0:
                    return
                time.sleep(0.05)
            if start_system_flag==0:
                return
            time.sleep((endtime - datetime.now()).seconds)

            if play_order_type == PlayOrderType.onebyone and i == programmers[len(programmers)-1]:
                return
            if play_order_type == PlayOrderType.singleloop and i != 0:
                return               

def update_signal(url,resource_broadcast_ip, resource_broadband_ip):
    global packet
    global sequence_number

    program_data = url_load(url)
    json_data=json.loads(program_data)
    if json_data['programmer']['sequence'] <= sequence_number: 
        return
    print "update file <" , url , "> successful \n"
    sequence_number = json_data['programmer']['sequence']
    packet['programmer']['sequence'] = sequence_number
    resources = json_data['programmer']['resources']
    for res in resources:
        for item in packet['programmer']['resources']:
            if item['id'] != res['id']: continue
            if item['sequence'] >= res['sequence']: break
            item['sequence'] = res['sequence']
            if item['type'] == 'broadcast' and res['type'] == 'broadband':
                ffplay_port = item['url'].split(':')[-1]
                ffmpeg_port = ffplay_port[:1] + '1' + ffplay_port[2:]
                item['url'] = 'smt://{0}:{1}@:{2}'.format(resource_broadband_ip, ffmpeg_port,ffplay_port)
                item['type'] = 'broadband'
            elif item['type'] == 'broadband' and res['type'] == 'broadcast':
                    ffplay_port = item['url'].split(':')[-1]
                    item['url'] = 'smt://{0}:{1}'.format(resource_broadcast_ip, ffplay_port)
                    item['type'] = 'broadcast'    
    print packet
            
            
def get_current_programme():
    return packet

if __name__ == "__main__":
    main()
