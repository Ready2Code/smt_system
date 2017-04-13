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

FNULL = open(os.devnull, 'w')
DEFAULT = object()

COMMAND_LISTEN_PORT = 9999
FFPLAY_LISTEN_PORT = 8080
CHANNEL_FILE = "../related/channels.json"

SCREEN_WIDTH = 3840
SCREEN_HEIGHT = 2160

programmer_changed = 0
sequence = 0
channels_info = dict()
continue_play_channel = '0'
is_continue_play = 0
pffplay = None
channel_info = {}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_screen_resolution():
    global SCREEN_WIDTH
    global SCREEN_HEIGHT 
    output = Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=PIPE).communicate()[0]
    resolution = output.split()[0].split(b'x')
    SCREEN_WIDTH = int(resolution[0])
    SCREEN_HEIGHT = int(resolution[1])
    print bcolors.UNDERLINE + 'screen resolution: '+ resolution[0]+ ' X '+ resolution[1] + bcolors.ENDC 

def cal_screen_value(val, is_width):
    if isinstance(val, int):
        return val
    else:
        p = float(val.split('%')[0]) / 100
        if is_width:
            return p * SCREEN_WIDTH
        else:
            return p * SCREEN_HEIGHT

def load(name):
    with open(name) as json_file:
        data = json.load(json_file)
        return data

def call_ffplay(res):
    global pffplay
    #print 'call_ffplay', res
    print 'res is ', res
    begintime = datetime.strptime(res['begin'], '%Y-%m-%dT%H:%M:%S.%f')
    endtime = datetime.strptime(res['end'], '%Y-%m-%dT%H:%M:%S.%f')
    res_type = res['type']
    delta = endtime - begintime
    ffplay_command = ''
    if(res_type == 'broadcast'):
        ffplay_command = '../related/ffplay {0},{1},{2},{3},{4} -port {5}'.format(res['url'],cal_screen_value(res['layout']['posx'], True), cal_screen_value(res['layout']['posy'], False), cal_screen_value(res['layout']['width'], True), cal_screen_value(res['layout']['height'], False), FFPLAY_LISTEN_PORT) 
    #print ffplay_command
    #p = Popen(shlex.split(ffplay_command))
    pffplay = Popen(shlex.split(ffplay_command), stdout=FNULL, stderr=STDOUT)
    # add 1 more second    
    time.sleep(delta.seconds + 1)
    print delta.seconds, "passed  resource [", res['name'], "] is closed"
    del_ffplay(res)


def add_ffplay(res):
    #print res
    begintime = datetime.strptime(res['begin'], '%Y-%m-%dT%H:%M:%S.%f')
    endtime = datetime.strptime(res['end'], '%Y-%m-%dT%H:%M:%S.%f')
    curr_time = datetime.now()
    #if(curr_time < begintime or curr_time > endtime):
    #    print 'cannot add this resource: time stamp is not valid'
    #    return
    url = res['url']
    server_ip = ''
    name = ''

    if '@' in url:
        server_ip = url.split('@')[0].split('://')[1]
        name = url.replace(server_ip, '')
    else:
        name = url
    
    add_command = {'type':'add', 'server': '', 'format': {'name': '','posx':'','posy':'','width':'','height':'','kind':'video'}}
    add_command['server'] = server_ip
    add_command['format']['name'] = name
    add_command['format']['posx'] = cal_screen_value(res['layout']['posx'], True)
    add_command['format']['posy'] = cal_screen_value(res['layout']['posy'], False)
    add_command['format']['width'] = cal_screen_value(res['layout']['width'], True)
    add_command['format']['height'] = cal_screen_value(res['layout']['height'], False)
    if is_continue_play == 1 and res['type'] == 'broadcast':
        add_command['format']['kind'] = 'all'
    addcommand = json.dumps(add_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(addcommand,("localhost", FFPLAY_LISTEN_PORT))
   
    delta = endtime - curr_time
    # add 1 more second 
    time.sleep(delta.seconds + 1)
    print delta.seconds, "passed  resource [", res['name'], "] is closed"
    del_ffplay(res)

def del_ffplay(res):
    server_ip = ''
    name = ''
    url = res['url']
    if(res['type'] == 'broadcast'):
        name = url
    else:
        server_ip = url.split('@')[0].split('://')[1]
        name = url.replace(server_ip, '')

    del_command = {'type':'del', 'server': '', 'format': {'name': ''}}
    del_command['server'] = server_ip
    del_command['format']['name'] = name
    delcommand = json.dumps(del_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(delcommand, ('localhost', FFPLAY_LISTEN_PORT))

def UDP_recv(port, channel_id, name):
    global sequence
    last_sequence = sequence
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    print bcolors.OKBLUE + "{2} id [{0}] is listened on port {1}".format(channel_id, port, name.encode('utf-8').strip()) + bcolors.ENDC

    while 1:
        data, address = s.recvfrom(4096)
        json_data = json.loads(data)
        channels_info[channel_id] = json_data

        if(is_continue_play and
            continue_play_channel == channel_id and
            json_data['programmer']['sequence'] > sequence):
            sequence = json_data['programmer']['sequence']
            play_json(json_data)

        if json_data['programmer']['sequence'] > last_sequence:
            last_sequence = json_data['programmer']['sequence']
            print bcolors.WARNING + "\n{1} id [{0}] have an updated signaling ...".format(channel_id, name.encode('utf-8').strip()) + bcolors.ENDC
        #print json_data
        #print current_json 

def COMMAND_recv(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('localhost', port))
    print bcolors.OKBLUE + "COMMAND is listening on port {0}".format(port) + bcolors.ENDC

    while 1:
        data, address = s.recvfrom(4096)
        json_data = json.loads(data) 
        print json_data
        print bcolors.WARNING + "receieve a new command:\n" + data +bcolors.ENDC
        
        if pffplay is None:
            t = Thread(target=call_ffplay, args=(json_data, ))
            t.start()
        else:
            t = Thread(target=add_ffplay, args=(json_data, ))
            t.start()

def play_json(json_data):
    #print 'play_json'
    if pffplay is None:
        for res in json_data['programmer']['resources']:
            if(res['type'] == 'broadcast'):
                t = Thread(target=call_ffplay, args=(res, ))
                t.setDaemon(True)
                t.start()
    else:
        for res in json_data['programmer']['resources']:
            if(res['type'] == 'broadcast'):
                t = Thread(target=add_ffplay, args=(res, ))
                t.setDaemon(True)
                t.start()

def handle_command(command):
    option = command.split(' ')

    print 'handle_command ',command
    if(option[0] not in options.keys()):
        return bcolors.FAIL + 'unknown command, use help' + bcolors.ENDC

    if len(option) == 2:
        options[option[0]](option[1])
    else:
        options[option[0]]()

def initial():
    global channel_info 
    channel_info = load(CHANNEL_FILE)

    # each channel is assigned one thread to handle its broadcast signaling
    for channel in channel_info['channels']:
        port = int(channel['url'].split(':')[-1])

        t = Thread(target=UDP_recv, args=(port,channel['id'],channel['name']))
        t.setDaemon(True)
        t.start()
        time.sleep(0.1)

    # start another thread to handle the command from other terminal like pad
    c = Thread(target=COMMAND_recv, args=(COMMAND_LISTEN_PORT,))
    c.setDaemon(True)
    c.start()
    time.sleep(0.1)

    print bcolors.UNDERLINE + "program succeed in starting up ... \n" + bcolors.ENDC
    print(get_screen_resolution())
 
def main():
    initial()
    while 1:
        command = raw_input(bcolors.BOLD +'Enter your command:  '+bcolors.ENDC)
        print handle_command(command)
        continue

##############################################################
def show_channels():
    for key, value in channels_info.iteritems():
        print bcolors.HEADER + "channel id [", key, "] :" + bcolors.ENDC
        print bcolors.OKBLUE + json.dumps(value, ensure_ascii=False,indent=4, sort_keys=True) + bcolors.ENDC

def show_channel(channel_id = DEFAULT):
    ret = object()
    if channel_id is DEFAULT:
        print bcolors.FAIL + "missing operand: need channel_id" + bcolors.ENDC
        return
    if channel_id not in channels_info.keys():
        print bcolors.FAIL + "unknown channel_id" + bcolors.ENDC
    else:
        print bcolors.OKBLUE + json.dumps(channels_info[channel_id], ensure_ascii=False,indent=4,sort_keys=True) + bcolors.ENDC
        ret = channels_info[channel_id] 
    return ret

def get_current_programme():
    global continue_play_channel
    return show_channel(continue_play_channel)

def play_programmer(val = DEFAULT):
    # to play the whole channel broadcast resources
    if val is DEFAULT:
        print bcolors.FAIL + "missing operand: need channel_id" + bcolors.ENDC
        return
    if ":" not in val:
        play_json(channels_info[val])
        return
        
    vals = val.split(':')
    if vals[0] not in channels_info.keys():
        print bcolors.FAIL + "unknown channel_id" + bcolors.ENDC
        return
    programmers = channels_info[vals[0]]
    for res in programmers['programmer']['resources']:
        if res['id'] == vals[1]:
            if(res['type'] == 'broadband'):
                 t = Thread(target=add_ffplay, args=(res, ))
                 t.setDaemon(True)
                 t.start()

def help():
    print bcolors.HEADER + 'all commands are listed:' + bcolors.ENDC
    for key  in sorted(options):
        print '-',key

def continue_play(channel = DEFAULT):
    if channel is DEFAULT:
        print bcolors.FAIL + "missing operand: need channel_id" + bcolors.ENDC
        return 
    global continue_play_channel
    global is_continue_play 
    continue_play_channel = channel
    is_continue_play = 1

def stop_all():
    global is_continue_play
    global pffplay
    global sequence
    is_continue_play = 0
    pffplay.kill()
    pffplay = None
    sequence = 0

def stop_play(val = DEFAULT):
    global pffplay
    if val is DEFAULT:
        print bcolors.FAIL + "missing operand: need channel_id" + bcolors.ENDC
        return
    if ":" not in val:
        pffplay.kill()
        pffplay = None
        return

    vals = val.split(':')
    if vals[0] not in channels_info.keys():
        print bcolors.FAIL + "unknown channel_id" + bcolors.ENDC
        return
    programmers = channels_info[vals[0]]
    for res in programmers['programmer']['resources']:
        if (res['id'] == vals[1]):
            if(res['type'] == 'broadband'):
                t = Thread(target=del_ffplay, args=(res, ))
                t.setDaemon(True)
                t.start()

def exit():
    print bcolors.OKGREEN + 'goodbye & have a good day...' + bcolors.ENDC
    os._exit(0)

options = { 'help':help,
            'channels':show_channels,
            'channel':show_channel,
            'play':play_programmer,
            'cplay':continue_play,
            'stopall':stop_all,
            'stop':stop_play,
            'exit':exit,
}





if __name__ == "__main__":
    main()
