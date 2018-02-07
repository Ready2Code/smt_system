#!/usr/bin/env python
# Minghao LI 2017-2-20
import json
import time
import re
import socket 
import sys
import urllib2
import shlex
import os
import platform
import thread
from datetime import datetime, timedelta
from threading import Timer, Thread, Event
from subprocess import call,Popen,PIPE,STDOUT
from utils import functions
from utils import smt_proto 
from utils import signal_format_converter 
from ntpclient import ntpthread

FNULL = open(os.devnull, 'w')
DEFAULT = object()

COMMAND_LISTEN_PORT = 9999
FFPLAY_LISTEN_PORT = 8080
PORT1 = 9431
PORT2 = 9430

def get_platform():
    try:
        import starglobal
        return starglobal.platform
    except:
        return platform.system()
		
if get_platform() == 'Android':
    RELATIVE_PATH = "/data/data/tv.danmaku.ijk.media.example/files/smt_system/related/"
else:
    RELATIVE_PATH = "../related/"
CHANNEL_FILE = "channels.json"

SCREEN_WIDTH = 3840
SCREEN_HEIGHT = 2160

is_gateway = 0
GATEWAY_IP_ADDR = '192.168.100.11'
GATEWAY_IP_LISTENING_PORT = 5005
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
last_res = {}
signal_thread = None
smtproto = smt_proto.SmtProto()
program_json_data = {}
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
    if get_platform() == "Linux":
        os.environ['DISPLAY'] = ':0.0'
        output = Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
        resolution = output.split()[0].split(b'x')
        SCREEN_WIDTH = int(resolution[0])
        SCREEN_HEIGHT = int(resolution[1])
    elif get_platform() == "Windows":
        output = Popen("wmic DESKTOPMONITOR get screenwidth, screenheight", shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
        resolution = output.split()
        SCREEN_WIDTH  = int(resolution[3])
        SCREEN_HEIGHT = int(resolution[2])
    else:
        print "Invalid platform type",get_platform()
    print 'screen resolution: '+ str(SCREEN_WIDTH)+ ' * '+ str(SCREEN_HEIGHT) 

# window ={'id': xxxxx, 'type': 'fullscreen' or 'normal'
def window_stack_push(wid, url, wtype='normal'):
    global window_stack_list
    for i in range(len(window_stack_list)-1,-1,-1):
        if window_stack_list[i]['id'] == wid:
            print "push fail" + wid + "already exists"
            return
    if wtype == 'fullscreen':
        for i in range(len(window_stack_list)-1,-1,-1):
            if window_stack_list[i]['type'] == 'fullscreen':
                window_stack_list[i]['type'] = 'normal'
                break
    window = {'id': wid, 'type': wtype, 'url':url}
    window_stack_list.append(window)
    print 'window_stack_list=',window_stack_list

def window_stack_pop(wid):
    global window_stack_list
    for i in range(len(window_stack_list)-1,-1,-1):
        if wid == window_stack_list[i]['id']:
            del window_stack_list[i]
            break

def window_stack_get():
    return window_stack_list

def window_stack_clean():
    window_stack_list = []

def window_stack_check_type(wid):
    global window_stack_list
    for i in range(len(window_stack_list)-1,-1,-1):
        if wid == window_stack_list[i]['id']:
            return window_stack_list[i]['type']
    return

def window_stack_fullscreen_type(wid):
    global window_stack_list
    for i in range(len(window_stack_list)-1,-1,-1):
        if wid == window_stack_list[i]['id']:
            if(window_stack_list[i]['type'] == 'fullscreen'):  window_stack_list[i]['type'] = 'normal'
            else: window_stack_list[i]['type'] = 'fullscreen'
        else:
            if(window_stack_list[i]['type'] == 'fullscreen'):  window_stack_list[i]['type'] = 'normal'


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

    ffplay_command = ''
    str_avlogext=''
    str_bk=''
    str_sync=''
    str_port=''
    #str_quick='-fflags nobuffer  -analyzeduration 100 -probesize 50 -framedrop '
    str_quick=' -analyzeduration 100 -probesize 50 -framedrop '
    str_type = ' -type ' + res_type

    if get_platform() == "Windows":
        ffplay_command = RELATIVE_PATH + 'ffplay.exe' + ' '
    if get_platform() == "Linux":
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
        ffplay_command =(ffplay_command + str_sync + str_avlogext + res['url'] + ' ' + str_port + str_bk + str_quick + str_type)

    print ffplay_command
    window_stack_clean()
    window_stack_push(res['id'],res['url'],'fullscreen')
    #p = Popen(shlex.split(ffplay_command))
    pffplay = ffplay_command

    if get_platform() == 'Android':
        send_cmd = "cal-" + res['url']
        control_player(send_cmd)

    ffplay_pid = ffplay_pid + 1
    try:
        thread.start_new_thread( os.system, (ffplay_command, ) )
    except:
        print "Error: unable to start thread"
    #pffplay = Popen(shlex.split(ffplay_command), stdout=FNULL, stderr=STDOUT)
    if(related == 'true'):
        time.sleep(2) 
        prompt_add()
    # add 1 more second    
    curr_time_with_timezone = datetime.now()
    curr_time = time_remove_timezone(curr_time_with_timezone)
    delta = endtime - curr_time 

    cur_ffplay_id = ffplay_pid
    time.sleep(delta.seconds)
    if res.has_key('name'):
        print delta.seconds, "passed  resource [", res['name'], "] is closed"
    else:
        print delta.seconds, "passed  resource [", res['id'], "] is closed"
    del_ffplay(res, cur_ffplay_id)

def time_remove_timezone(stime, zone_offset='default'):
    if 'default' == zone_offset:
        now_stamp = time.time()
        local_time = datetime.fromtimestamp(now_stamp)
        utc_time = datetime.utcfromtimestamp(now_stamp)
        zone_offset = local_time - utc_time
    time_with_zone_offset = stime - zone_offset
    return time_with_zone_offset 

def get_ip_and_name_from_url(url):
    server_ip = ''
    name = ''
    if '@' in url:
        server_ip = url.split('@')[0].split('://')[1]
        name = url.replace(server_ip, '')
        name = name.replace('@', '')
    else:
        name = url
    return (server_ip, name)


def add_ffplay(res, full = DEFAULT):
    #print res
    global related
    global ffplay_pid
    begintime = datetime.strptime(res['begin'], '%Y-%m-%dT%H:%M:%S.%f')
    endtime = datetime.strptime(res['end'], '%Y-%m-%dT%H:%M:%S.%f')
    curr_time_with_timezone = datetime.now()
    curr_time = time_remove_timezone(curr_time_with_timezone)
    #if(curr_time < begintime or curr_time > endtime):
    #    print 'cannot add this resource: time stamp is not valid'
    #    return
    url = res['url']
    server_ip = ''
    name = ''
    (server_ip, name) = get_ip_and_name_from_url(url)
    add_command = {'type':'add', 'server': '', 'format': {'name': '', 'type':'','fullscreen':'','posx':'','posy':'','width':'','height':'','kind':'video'}}
    add_command['server'] = server_ip
    add_command['format']['name'] = name
    add_command['format']['type'] = res['type']
    if full == 'full': 
        add_command['format']['fullscreen'] = 1
        add_command['format']['kind'] = 'all'
        window_stack_push(res['id'], res['url'], 'fullscreen')        
    else: 
        add_command['format']['fullscreen'] = 0
        add_command['format']['kind'] = 'video'
        window_stack_push(res['id'], res['url'], 'normal')
    add_command['format']['posx'] = cal_screen_value(res['layout']['posx'], True)
    add_command['format']['posy'] = cal_screen_value(res['layout']['posy'], False)
    add_command['format']['width'] = cal_screen_value(res['layout']['width'], True)
    add_command['format']['height'] = cal_screen_value(res['layout']['height'], False)
    addcommand = json.dumps(add_command)
    if get_platform() == 'Android':
        send_cmd = "add-" + name
        control_player(send_cmd)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print "addcommand=%s" % addcommand
        s.sendto(addcommand,("localhost", FFPLAY_LISTEN_PORT))



    if(related == 'true'):
        time.sleep(2)
        prompt_add()
    delta = endtime - curr_time
        # add 1 more second 
    cur_ffplay_id = ffplay_pid
    time.sleep(delta.seconds)
    print delta.seconds, "passed  resource [", res['name'], "] is closed"
    del_ffplay(res, cur_ffplay_id)

def del_ffplay(res, pid=0):
    global ffplay_pid
    server_ip = ''
    name = ''
    url = res['url']
    if(pid !=0 and pid !=ffplay_pid):
        return
    (server_ip, name) = get_ip_and_name_from_url(url)

    # full screen cannot be closed
    if cal_screen_value(res['layout']['width'], True) == SCREEN_WIDTH and cal_screen_value(res['layout']['height'], False) == SCREEN_HEIGHT:  return
    if window_stack_check_type(res['id']) == 'fullscreen' : return 
    window_stack_pop(res['id'])
    if(related == 'true'):    prompt_del()
    del_command = {'type':'del', 'server': '', 'format': {'name': ''}}
    del_command['server'] = server_ip
    del_command['format']['name'] = name
    delcommand = json.dumps(del_command)
    if get_platform() != 'Android':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(delcommand, ('localhost', FFPLAY_LISTEN_PORT))
    else:
        send_cmd = "del-" + name
        control_player(send_cmd)

def prompt_add():    
    add_command = {'type':'reddot','format': {'name': ''}}
    addcommand = json.dumps(add_command)
    if get_platform() != 'Android':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(addcommand,("localhost", FFPLAY_LISTEN_PORT))
    else:
        send_cmd = "reddot-" + " "
        image_player(send_cmd)

def prompt_del():
    prompt_add()

def type_update(res, orig):    
    add_command = {'type':'type','format': {'orig': orig,'name':res['url'],'type': res['type']}}
    addcommand = json.dumps(add_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(addcommand,("localhost", FFPLAY_LISTEN_PORT))

def fullscreen(res):    
    full_command = {'type':'full','format': {'name': res['url']}}
    fullcommand = json.dumps(full_command)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(fullcommand,("localhost", FFPLAY_LISTEN_PORT))

def get_time_second(time):
    timearr= re.split(":",time)  
    minute=int(timearr[1])*60
    second=float(timearr[2])
    cur_time=minute+second
    return cur_time
def show_embeded_img(json_data):
    ntp_status = ntpthread.ntp_status
    if ntp_status=='stop':
       ntp_status=0.0
    ntp_status = float(ntp_status)
    if json_data.has_key('programmer'):
      if json_data['programmer'].has_key('external_resources'):
       for res in json_data['programmer']['resources']:
         if res.has_key('info') and res['info'] == 'embeded_ad':
          begin_time=res['begin']
          end_time=res['end']
          now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
          nowtime= get_time_second(now_time) + ntp_status
          ad_begintime= get_time_second(begin_time)
          ad_endtime= get_time_second(end_time)
          diff=nowtime - ad_begintime
          if diff >= -1 and diff <=0:
             res['display']='1'
          else:
             res['display']='0'
    return json_data

def control_embeded_ad__reddot_display(json_data):
    ntp_status = ntpthread.ntp_status
    if ntp_status=='stop':
       ntp_status=0.0
    ntp_status = float(ntp_status)
    global related
    if json_data['programmer']['sequence']  > 0:
        for res in json_data['programmer']['resources']:
            if res.has_key('info') and res['info'] == 'embeded_ad':
                begin_time=res['begin']
                end_time=res['end']
                now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                nowtime= get_time_second(now_time) + ntp_status
                ad_begintime= get_time_second(begin_time)
                ad_endtime= get_time_second(end_time)
                diff=nowtime - ad_begintime
                diff2=nowtime - ad_endtime
#       print "name ===================================\n",res['name']
#         print "begintime ===================================\n",begin_time
#         print "endtime ===================================\n", end_time
#         print "now_time===================================\n" ,nowtime
#         print "diff===================================\n" ,diff
#         print "diff2===================================\n" ,diff2
                if diff > -2 and diff < 1:
                    related='true'
                    prompt_add()
                if diff2 > 0 and related=='true':
                    related='false'
                    prompt_del()

def UDP_recv(port, channel_id, name):
    global sequence
    global related
    global channels_info
    global last_res
    global smtproto
    global program_json_data
    last_sequence = sequence
    last_id = ""
    last_begintime = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'binding sigalling port=%d' % port
    s.bind(('', port))
    print bcolors.OKBLUE + "{2} id [{0}] is listened on port {1}".format(channel_id, port, name.encode('utf-8').strip()) + bcolors.ENDC


    while 1:
#data, address = s.recvfrom(4096)
        data, address = s.recvfrom(65535)
        json_data = {}
        try:
            json_data = json.loads(data)
        except:
            if smtproto.process_smtp_data(data):
                json_data = signal_format_converter.PA_message_to_program(smtproto.message["PA_message"])
            else:
                continue
        program_json_data = json_data
        control_embeded_ad__reddot_display(json_data)
        
        ## Heart beat
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto('add' , (GATEWAY_IP_ADDR, GATEWAY_IP_LISTENING_PORT))
        
        if is_gateway == 1 and json_data['programmer']['sequence'] > 0:
            for res in json_data['programmer']['resources']:
                if(res['type'] == 'broadcast'):
                    res['url'] = res['url'][:6]+GATEWAY_IP_ADDR+':'+str(GATEWAY_IP_PORT)+'@'+res['url'][6:]        	
        channels_info[channel_id] = json_data

        if json_data['programmer']['sequence']  == 0:
            clear_all()
            progress = (100 * json_data['counter']) if json_data.has_key('counter') else 0
            print "*********** restart   %.1f%%  **************" % progress
            continue

        if(is_continue_play and
           continue_play_channel == channel_id and
           json_data['programmer']['sequence'] > sequence and
           json_data['programmer']['begin'] != last_begintime ):
            sequence = json_data['programmer']['sequence']
            last_begintime = json_data['programmer']['begin']
            play_json(json_data)

        if json_data['programmer']['sequence'] > last_sequence:
            last_sequence = json_data['programmer']['sequence']
            print bcolors.WARNING + "\n{1} id [{0}] have an updated signaling ...".format(channel_id, name.encode('utf-8').strip()) + bcolors.ENDC
            if 'related' in json_data['programmer'].keys(): 
                related = json_data['programmer']['related']
            for res in json_data['programmer']['resources']:
                if len(last_res) == 0:
                    break
                if res['type'] == "broadcast":
                    for ll in last_res:
                        if res['id'] == ll['id'] and ll['type'] == "broadband":
                            type_update(res, ll['url'])
                            break
                else: 
                    for ll in last_res:
                        if res['id'] == ll['id'] and ll['type'] == 'broadcast':
                            type_update(res, ll['url'])
                            break

        last_res = json_data['programmer']['resources']
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

def control_player(ccmd):
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.sendto(ccmd, ('localhost', PORT1))
    print "Success send ...", ccmd
    s1.close()
def image_player(ccmd):
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2.sendto(ccmd, ('localhost', PORT2))
    print "Image Success send ...", ccmd
    s2.close()

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

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto('add' , (GATEWAY_IP_ADDR, GATEWAY_IP_LISTENING_PORT))

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
        signal_thread = t
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
    ret = {}
    if channel_id is DEFAULT:
        print bcolors.FAIL + "missing operand: need channel_id" + bcolors.ENDC
        return ret 
    if channel_id not in channels_info.keys():
        print bcolors.FAIL + "unknown channel_id" + bcolors.ENDC
    else:
        #print bcolors.OKBLUE + json.dumps(channels_info[channel_id], ensure_ascii=False,indent=4,sort_keys=True) + bcolors.ENDC
        ret = channels_info[channel_id] 
    return ret

def get_current_programme():
    global continue_play_channel
    cur_programme = show_channel(continue_play_channel)
    window_stack = window_stack_get()
    if cur_programme.has_key('programmer'):
        cur_programme['programmer']['window_stack'] = window_stack
    cur_programme=show_embeded_img(cur_programme) 
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
    related = programmers['programmer']['related'] if programmers['programmer'].has_key('related') else ''
    for res in programmers['programmer']['resources']:
        if res['id'] == vals[1]:
            if('exception' in res.keys()):
                exception = vals[0] + ':' + res['exception']
            else:
                exception = ''

            if pffplay is not None:
                if(window_stack_check_type(res['id']) == 'normal' and full == 'full'):
                    fullscreen(res)
                    window_stack_fullscreen_type(res['id'])
                elif window_stack_check_type(res['id']) == 'fullscreen':
                    print 'invalid operations. full screen cannot be changed to normal.'
                else:
                    t = Thread(target=add_ffplay, args=(res, full))
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
    if get_platform() != 'Android':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(rendercommand,("localhost", FFPLAY_LISTEN_PORT))
    else:
        send_cmd = "render-render"
        control_player(send_cmd)

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
