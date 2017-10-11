#!/usr/bin/env python
# Minghao LI 2017-2-20
import json
import time
import socket 
import sys
import urllib2
import shlex
import os
import platform
from datetime import datetime, timedelta
from threading import Timer, Thread, Event
from subprocess import call,Popen,PIPE,STDOUT
from utils import functions


FNULL = open(os.devnull, 'w')
DEFAULT = object()

COMMAND_LISTEN_PORT = 9999
FFPLAY_LISTEN_PORT = 8080
RELATIVE_PATH = "../related/"
CHANNEL_FILE = "channels.json"

SCREEN_WIDTH = 3840
SCREEN_HEIGHT = 2160

is_gateway = 1
GATEWAY_IP_ADDR = '192.168.100.11'
GATEWAY_IP_PORT = 8000
LOCAL_IP_ADDR = '192.168.100.244'

programmer_changed = 0
sequence = 0
channels_info = dict()
continue_play_channel = '0'
is_continue_play = 0
pffplay = None
ffplay_pid = 0    #to distinguish ffplay, it is not a true process ID
related = 'false'
exception = ''
channel_info = {}
g_info_collector_dest = ''
g_device_name = ''
g_sync='smt'
window_stack_list = []

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
    if platform.system() == "Linux":
        os.environ['DISPLAY'] = ':0.0'
        output = Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
        resolution = output.split()[0].split(b'x')
        SCREEN_WIDTH = int(resolution[0])
        SCREEN_HEIGHT = int(resolution[1])
    elif platform.system() == "Windows":
        output = Popen("wmic DESKTOPMONITOR get screenwidth, screenheight", shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
        resolution = output.split()
        SCREEN_WIDTH  = int(resolution[3])
        SCREEN_HEIGHT = int(resolution[2])
    else:
        print "can't get platform type"
    print 'screen resolution: '+ str(SCREEN_WIDTH)+ ' * '+ str(SCREEN_HEIGHT) 

# window ={'id': xxxxx, 'type': 'fullscreen' or 'normal'
def window_stack_push(wid, wtype='normal'):
    global window_stack_list
    window = {'id': wid, 'type': wtype}
    window_stack_list.append(window)

def window_stack_pop(wid=''):
    global window_stack_list
    for i in range(len(window_stack_list)-1,-1,-1):
        if wid == '' or wid == window_stack_list[i]['id']:
            del window_stack_list[i]
            break

def window_stack_get():
    return window_stack_list

def window_stack_clean():
    window_stack_list = []


           
     
def cal_screen_value(val, is_width = True):
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
    global related
    global ffplay_pid
    global g_sync
    #print 'call_ffplay', res
    print 'res is ', res
    begintime = datetime.strptime(res['begin'], '%Y-%m-%dT%H:%M:%S.%f')
    endtime = datetime.strptime(res['end'], '%Y-%m-%dT%H:%M:%S.%f')
    res_type = res['type']
    delta = endtime - begintime
    ffplay_command = ''
    str_avlogext=''
    str_bk=''
    str_sync=''
    str_port=''
    #str_quick='-fflags nobuffer  -analyzeduration 100 -probesize 50 -framedrop '
    str_quick=' -analyzeduration 100 -probesize 50 -framedrop '
        
    if platform.system() == "Windows":
        ffplay_command = RELATIVE_PATH + 'ffplay.exe' + ' '
    if platform.system() == "Linux":
        ffplay_command = RELATIVE_PATH + 'ffplay' + ' '

    if g_info_collector_dest != '' and g_device_name != '':
        str_avlogext = '-avlogext ' + g_info_collector_dest + ' -deviceinfo ' + g_device_name + ' '


    if g_sync != '':
        str_sync='-sync ' + g_sync + ' '

    str_port ='-port '+ str(FFPLAY_LISTEN_PORT)+ ' '
    if(res_type == 'broadcast'):
        #-sync smt 
        if ('bk' in res.keys()):
            str_bk = '-bk '+ res['bk'] + ' '
        ffplay_command =(ffplay_command + str_sync + str_avlogext + res['url'] + ',' 
                                        + str(cal_screen_value(res['layout']['posx'], True))   + ',' 
                                        + str(cal_screen_value(res['layout']['posy'], False))  + ',' 
                                        + str(cal_screen_value(res['layout']['width'], True))  + ','
                                        + str(cal_screen_value(res['layout']['height'], False))+ ' '
                                        + str_port + str_bk + str_quick)
 

    print ffplay_command
    window_stack_clean()
    window_stack_push(res['id'],'fullscreen')
    #p = Popen(shlex.split(ffplay_command))
    pffplay = ffplay_command
    ffplay_pid = ffplay_pid + 1
    os.system(ffplay_command)
    #pffplay = Popen(shlex.split(ffplay_command), stdout=FNULL, stderr=STDOUT)
    if(related == 'true'):
        time.sleep(2) 
        prompt_add()
    # add 1 more second    
    cur_ffplay_id = ffplay_pid
    time.sleep(delta.seconds + 1)
    print delta.seconds, "passed  resource [", res['name'], "] is closed"
    del_ffplay(res, cur_ffplay_id)


def add_ffplay(res):
    #print res
    global related
    global ffplay_pid
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
    if add_command['format']['width'] == SCREEN_WIDTH and add_command['format']['height'] == SCREEN_HEIGHT:
        add_command['format']['kind'] = 'all'
        window_stack_push(res[id], 'fullscreen')
    else:
        window_stack_push(res[id], 'normal')
    addcommand = json.dumps(add_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print "addcommand=%s" % addcommand
    s.sendto(addcommand,("localhost", FFPLAY_LISTEN_PORT))

    if(related == 'true'):
        time.sleep(2)
        prompt_add()
    delta = endtime - curr_time
    # add 1 more second 
    cur_ffplay_id = ffplay_pid
    time.sleep(delta.seconds + 1)
    print delta.seconds, "passed  resource [", res['name'], "] is closed"
    del_ffplay(res, cur_ffplay_id)

def del_ffplay(res, pid=0):
    global ffplay_pid
    server_ip = ''
    name = ''
    url = res['url']
    if(pid !=0 and pid !=ffplay_pid):
        return
    if(res['type'] == 'broadcast'):
        #wrong pid, ffplay has been killed
        name = url
    else:
        server_ip = url.split('@')[0].split('://')[1]
        name = url.replace(server_ip, '')

    window_stack_pop(res[id])
    if(related == 'true'):    prompt_del()
    del_command = {'type':'del', 'server': '', 'format': {'name': ''}}
    del_command['server'] = server_ip
    del_command['format']['name'] = name
    delcommand = json.dumps(del_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(delcommand, ('localhost', FFPLAY_LISTEN_PORT))

def prompt_add():    
    add_command = {'type':'reddot','format': {'name': ''}}
    addcommand = json.dumps(add_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(addcommand,("localhost", FFPLAY_LISTEN_PORT))

def prompt_del():
    prompt_add()

def UDP_recv(port, channel_id, name):
    global sequence
    global related
    global channels_info
    last_sequence = sequence
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    print bcolors.OKBLUE + "{2} id [{0}] is listened on port {1}".format(channel_id, port, name.encode('utf-8').strip()) + bcolors.ENDC

    while 1:
        data, address = s.recvfrom(4096)
        json_data = json.loads(data)
        if is_gateway == 1 and json_data['programmer']['sequence'] > 0:
            for res in json_data['programmer']['resources']:
                if(res['type'] == 'broadcast'):
                    res['url'] = res['url'][:6]+GATEWAY_IP_ADDR+':'+str(GATEWAY_IP_PORT)+'@'+res['url'][6:]        	
        channels_info[channel_id] = json_data

        if json_data['programmer']['sequence']  == 0:
            clear_all()
            print "*********** restart **************"
            continue

        if(is_continue_play and
           continue_play_channel == channel_id and
           json_data['programmer']['sequence'] > sequence):
            sequence = json_data['programmer']['sequence']
            play_json(json_data)

        if json_data['programmer']['sequence'] > last_sequence:
            last_sequence = json_data['programmer']['sequence']
            print bcolors.WARNING + "\n{1} id [{0}] have an updated signaling ...".format(channel_id, name.encode('utf-8').strip()) + bcolors.ENDC
            if 'related' in json_data['programmer'].keys(): 
                related = json_data['programmer']['related']
                # if related == 'true' and pffplay is not None:
                #    t = Thread(target=prompt_add)
                    #   t.start()
                # if related == 'false' and pffplay is not None:
                #    t = Thread(target=prompt_del)
                    #   t.start()                
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
    global pffplay
    if pffplay is None:
        for res in json_data['programmer']['resources']:
            if(res['type'] == 'broadcast'):
                t = Thread(target=call_ffplay, args=(res, ))
                t.setDaemon(True)
                t.start()
                break
    else:
        for res in json_data['programmer']['resources']:
            if(res['type'] == 'broadcast'):
                t = Thread(target=add_ffplay, args=(res, ))
                t.setDaemon(True)
                t.start()
                break

    if 'related' in json_data['programmer'].keys(): 
        related = json_data['programmer']['related']
        print "red dot"
        time.sleep(2)
        if related == 'true' and pffplay is not None:
            print "show dot"
            t = Thread(target=prompt_add)
            t.start()

def exception():
    global exception
    print "exception exit, starting another stream"
    if(exception != ''):
        play_programmer(exception)


def handle_command(command):
    option = command.split(' ')

    if(option[0] not in options.keys()):
        print bcolors.FAIL + 'unknown command, use help' + bcolors.ENDC
        return

    if len(option) == 2:
        options[option[0]](option[1])
    elif len(option) == 3:
        options[option[0]](option[1],option[2])
    else:
        options[option[0]]()

def initial(info_collector_dest='', device_name=''):
    global channel_info 
    global g_info_collector_dest
    global g_device_name

    g_info_collector_dest = info_collector_dest
    g_device_name = device_name
    channel_info = load(RELATIVE_PATH + CHANNEL_FILE)

    # each channel is assigned one thread to handle its broadcast signaling
    for channel in channel_info['channels']:
        port = int(channel['url'].split(':')[-1])

        if is_gateway == 1:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto('add '+ LOCAL_IP_ADDR + ':' + str(port) , (GATEWAY_IP_ADDR, GATEWAY_IP_PORT))

        t = Thread(target=UDP_recv, args=(port,channel['id'],channel['name']))
        t.setDaemon(True)
        t.start()
        time.sleep(0.1)

    # start another thread to handle the command from other terminal like pad
    c = Thread(target=COMMAND_recv, args=(COMMAND_LISTEN_PORT,))
    c.setDaemon(True)
    c.start()
    time.sleep(0.1)

    get_screen_resolution()
    print bcolors.UNDERLINE + "program succeed in starting up ... \n" + bcolors.ENDC


def main():
    initial()
    while 1:
        command = raw_input(bcolors.BOLD +'Enter your command:  '+bcolors.ENDC)
        handle_command(command)
        continue

##############################################################
def show_channels():
    global channels_info
    for key, value in channels_info.iteritems():
        print bcolors.HEADER + "channel id [", key, "] :" + bcolors.ENDC
        print bcolors.OKBLUE + json.dumps(value, ensure_ascii=False,indent=4, sort_keys=True) + bcolors.ENDC

def show_channel(channel_id = DEFAULT):
    global channels_info
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
    cur_programme = show_channel(continue_play_channel)
    window_stack = window_stack_get()
    cur_programme['programmer']['window_stack'] = window_stack 
    return cur_programme

def play_programmer(val = DEFAULT, full = DEFAULT):
    global related
    global exception
    global channels_info
    # to play the whole channel broadcast resources
    if val is DEFAULT:
        print bcolors.FAIL + "missing operand: need channel_id" + bcolors.ENDC
        return

    if ":" not in val:
        if val not in channels_info.keys():
            print bcolors.FAIL + "wrong channel_id: no such channel_id" + bcolors.ENDC
            return     
        play_json(channels_info[val])
        return

    vals = val.split(':')
    if vals[0] not in channels_info.keys():
        print bcolors.FAIL + "unknown channel_id" + bcolors.ENDC
        return
    programmers = channels_info[vals[0]]
    related = programmers['programmer']['related']
    for res in programmers['programmer']['resources']:
        if res['id'] == vals[1]:
            if('exception' in res.keys()):
                exception = vals[0] + ':' + res['exception']
            else:
                exception = ''

            if full == 'full':
                res['layout']['posx'] = 0
                res['layout']['posy'] = 0
                res['layout']['width'] = '100%'
                res['layout']['height'] = '100%'            
            if pffplay is not None:
                t = Thread(target=add_ffplay, args=(res, ))
                t.setDaemon(True)
                t.start()
            else:
                t = Thread(target=call_ffplay, args=(res, ))
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



def clear_all():
    global pffplay
    global sequence
    try:
        functions.kill_process_by_name(pffplay) 
        #pffplay.kill()
    except:
        pass
    os.system("pkill ffplay")
    pffplay = None
    sequence = 0

def stop_all():
    global is_continue_play
    is_continue_play = 0
    clear_all()

def stop_play(val = DEFAULT):
    global pffplay
    global ffplay_pid
    global channels_info
    if val is DEFAULT:
        print bcolors.FAIL + "missing operand: need channel_id" + bcolors.ENDC
        return
    if ":" not in val:
        functions.kill_process_by_name(pffplay) 
        #pffplay.kill()
        pffplay = None
        return

    vals = val.split(':')
    if vals[0] not in channels_info.keys():
        print bcolors.FAIL + "unknown channel_id" + bcolors.ENDC
        return
    programmers = channels_info[vals[0]]
    for res in programmers['programmer']['resources']:
        if (res['id'] == vals[1]):
            #if(res['type'] == 'broadband'):
            t = Thread(target=del_ffplay, args=(res, ffplay_pid))
            t.setDaemon(True)
            t.start()

def render():
    render_command = {'type':'render','format': {'name': ''}}
    rendercommand = json.dumps(render_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(rendercommand,("localhost", FFPLAY_LISTEN_PORT))


def exit():
    print bcolors.OKGREEN + 'goodbye & have a good day...' + bcolors.ENDC
    os._exit(0)

options = { 'help':help,
            'except':exception,
            'channels':show_channels,
            'channel':show_channel,
            'play':play_programmer,
            'cplay':continue_play,
            'stopall':stop_all,
            'stop':stop_play,
            'render':render,
            'prompt':prompt_add,
            'hide':prompt_del,
            'exit':exit,
}





if __name__ == "__main__":
    main()
