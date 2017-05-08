#!/usr/bin/env python
# Minghao LI 2017-2-20
import json
import time
import socket 
import sys
import urllib2
import shlex
import os
from datetime import datetime, timedelta
from threading import Timer, Thread, Event
from subprocess import call,Popen,PIPE,STDOUT
from itertools import cycle

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('20110101','%Y%m%d')

FNULL = open(os.devnull, 'w')

LOCAL_PORT = 8001
FILE_RELATIVE_PATH = './'
CHANNEL_FILE_NAME = '../related/channels.json'
CONFIG_FILE_NAME = 'programs.json'
DESTINATION_IP = '127.0.0.1'
#DESTINATION_IP = '192.168.1.212'

BROADCASE_TIME_INTERVAL = 0.5   #seconds

RESERVED_POS_ONE = 1
RESERVED_POS_TWO = 0
CHANNEL_NUM = 1
BROADBAND_SERVER_IP = '127.0.0.1'
#BROADCAST_SERVER_IP = '239.1.1.1'
BROADCAST_SERVER_IP = '127.0.0.1'

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

class SignalTimerThread(Thread):
    def __init__(self, event, dest):
        Thread.__init__(self)
        self.stopped = event
        self.dest = dest

    def run(self):
        while not self.stopped.wait(BROADCASE_TIME_INTERVAL):
            delay_broadcast(s, packet, self.dest)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def load(name):
    name = FILE_RELATIVE_PATH + name
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

def convert_signal(json_file, resource_broadcast_ip, resource_broadband_ip):
    global resource_num
    global sequence_number
    global packet
    json_data = json.loads(json_file)
    sequence_number += json_data['programmer']['sequence']
    json_data['programmer']['sequence'] = sequence_number
    json_data['programmer']['begin'] = update_delta_time(json_data['programmer']['begin'], endtime)
    json_data['programmer']['end'] = update_delta_time(json_data['programmer']['end'], endtime)

    resources = json_data['programmer']['resources']
    for res in resources:
        localfile = ''
        if ('url' in res.keys()): localfile = res['url']
        elif ('playlist' in res.keys()): localfile = res['playlist']
        if(localfile == ''): print 'error url or playlist has to been assigned' 
        if localfile.encode('ascii', 'ignore').startswith('./'):
            localfile = localfile.replace('./', FILE_RELATIVE_PATH)
        ffplay_port = '{0}{1}{2}{3}{4}'.format(RESERVED_POS_ONE,RESERVED_POS_TWO, CHANNEL_NUM, program_num, resource_num)
        ffmpeg_port = '{0}{1}{2}{3}{4}'.format(RESERVED_POS_ONE, 1, CHANNEL_NUM, program_num, resource_num)
        if(res['type'] == 'broadcast'):
            res['url'] = 'smt://{0}:{1}'.format(resource_broadcast_ip, ffplay_port)
        elif(res['type'] == 'broadband'):
            res['url'] = 'smt://{0}:{1}@:{2}'.format(resource_broadband_ip, ffmpeg_port,ffplay_port)
        else:
            print 'error unknown type in resources'

        res['begin'] = update_delta_time(res['begin'], endtime)
        res['end'] = update_delta_time(res['end'], endtime)

        print str(res['begin'])

        t = Thread(target=call_ffmpeg, args=(localfile, res, ffmpeg_port, resource_broadcast_ip, ffplay_port))
        t.daemon = True
        t.start()
        resource_num += 1
        resource_num = resource_num % 10
    return json_data

def call_ffmpeg(file_dir, res, port, resource_broadcast_ip, ffplay_port):
    time.sleep(aheadtime/1000)
    begintime = res['begin'].strftime('%Y-%m-%dT%H:%M:%S.%f')
    res_type = res['type']
    delta = res['end'] - datetime.now()
    ffmpeg_command = ''
    playlist = ''
    if('playlist' in res.keys()): playlist = '-f concat'
    if(res_type == 'broadcast'):
        ffmpeg_command = '../related/ffmpeg -re {4} -i {0} -begintime {1} -c:v copy -c:a aac -f mpu smt://{2}:{3}'.format(file_dir, begintime, resource_broadcast_ip, ffplay_port, playlist)
    elif(res_type == 'broadband'):
        ffmpeg_command = '../related/ffmpeg -re -port {1} {5} -i {0} -begintime {2} -c:v copy -c:a aac -f mpu smt://{3}:{4}'.format(file_dir, port, begintime, BROADBAND_SERVER_IP, 1, playlist) 
    print ffmpeg_command
    #p = Popen(shlex.split(ffmpeg_command))
    p = Popen(shlex.split(ffmpeg_command), stdout=FNULL, stderr=STDOUT)
    time.sleep(delta.seconds+1)
    print delta.seconds, "passed  resource [", res['name'], "] is closed"
    p.kill()

def delay_broadcast(s, packet, des):
    if len(packet) == 0:
        return

    cur = datetime.now()
    if ( cur > packet['programmer']['begin'] - timedelta(milliseconds=(aheadtime+cachetime)) and cur < packet['programmer']['end'] - timedelta(milliseconds=(aheadtime+cachetime))):
        #print 'Dest:',des,' Duration:', packet['programmer']['begin'], '~', packet['programmer']['end'],' Now:', datetime.now(), 'SIGNAL sending ', packet['programmer']['name']
        sp = json.dumps(packet, cls=DateTimeEncoder)#.encode('utf8')
        s.sendto(sp, des)
        #print sp
    else:
        print 'no proper signal to send...'
        #pass

def main():
    if len(sys.argv) != 4 and len(sys.argv) != 1:
        print 'Usage: %s <port> <programs.json> <destination>' % sys.argv[0]
        print '       or leave the parameters empty'
        return

    global program_num
    global resource_num
    global packet
    global endtime
    #global destination
    global aheadtime
    global cachetime

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
                     resource_broadband_ip = BROADBAND_SERVER_IP ):
    global program_num
    global resource_num
    global packet
    global endtime
    global destination
    global aheadtime
    global cachetime
    global programmers 

    #destination = destip
    json_data = load(programs_file)
    print "load file <" , programs_file , "> successful \n"

    signal_destination = (signal_destip, int(signal_port))
    aheadtime = json_data['aheadtime']
    cachetime = json_data['cachetime']
    programmers = json_data['programmers']
    print 'aheadtime =', aheadtime , 'cachetime =', cachetime

    stopFlag = Event()
    thread = SignalTimerThread(stopFlag, signal_destination)
    thread.setDaemon(True)
    thread.start()

    for i in cycle(programmers):
        url = i['url']
        print "processing", i['name'], url
        program_data = url_load(url)
        #print json.loads(program_data) 
        resource_num = 1
        convert = convert_signal(program_data, resource_broadcast_ip, resource_broadband_ip)
        packet = convert
        #print convert
        endtime = convert['programmer']['end'] - timedelta(milliseconds=(aheadtime+cachetime))
        print 'endtime = ', endtime
        time.sleep((endtime - datetime.now()).seconds)
        program_num += 1
        program_num = program % 10



if __name__ == "__main__":
    main()
