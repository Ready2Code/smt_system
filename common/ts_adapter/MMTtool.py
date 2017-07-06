# -*- coding: utf-8 -*-
from ctypes import *
import thread
from threading import Thread
import os
import re

dll_list={}

def find_process_by_name(name):
    name = name.replace('-',' ')
    name_list = name.split()
    cmd='ps aux | grep %s'%'| grep '.join(name_list) 
    f=os.popen(cmd)
    txt=f.read()
    if len(txt)<5:
        print 'there is no thread by name or command %s'%name
        return ''
    return txt

def kill_process_by_name(name):
    txt = find_process_by_name(name)
    regex=re.compile(r'\w+\s+(\d+)\s+.*')
    ids=regex.findall(txt)
    cmd="kill %s"%' '.join(ids)
    print cmd
    os.system(cmd)


def init():
    dll = CDLL("../related/libMMTtool.so")
    return dll

def get_ip_and_port_from_addr(addr):
    pos = addr.find(':')
    if -1 == pos:
        print "Invalid addr , NO ':', addr=",addr
        return 0
    try:
        addr_tuple =  (addr[:pos], int(addr[pos+1:]))
    except:
        print "Invalid addr, addr=",addr
        return 0
    return addr_tuple 

def ts_adapter_process(mode, srcaddr, destaddr):
    ts_adapter_thread(mode, srcaddr, destaddr)
    #t = Process(target=ts_adapter_thread,args=(mode, srcaddr, destaddr))
    #t.setDaemon(True)
    #t.start()
 

def ts_adapter_thread(mode, srcaddr, destaddr):
    global dll_list
    srcaddr_tuple=get_ip_and_port_from_addr(srcaddr)
    destaddr_tuple=get_ip_and_port_from_addr(destaddr)
    command = "../related/MMTtool "
    command = command + " --"+ mode
    command = command + " --"+ "srcip " + srcaddr_tuple[0]
    command = command + " --"+ "srcport " + str(srcaddr_tuple[1])
    command = command + " --"+ "dstip " + destaddr_tuple[0]
    command = command + " --"+ "dstport " + str(destaddr_tuple[1])
    print command
    dll_list[srcaddr] = command 
    try:
        os.system(command)
        #p = Popen(shlex.split(ffmpeg_command), stdout=FNULL, stderr=FNULL)
    except:
        return

def start_ts_adapter(mode, srcaddr, destaddr):
    global dll_list 
    if dll_list.has_key(srcaddr):
        return
    t = Thread(target=ts_adapter_process,args=(mode, srcaddr, destaddr))
    t.setDaemon(True)
    t.start()

def stop_ts_adapter(srcaddr):
    global dll_list 
    if dll_list.has_key(srcaddr):
        kill_process_by_name(dll_list[srcaddr])
        del dll_list[srcaddr]

def find_ts_adapter(srcaddr):
    global dll_list 
    txt = ''
    if dll_list.has_key(srcaddr):
        txt = find_process_by_name(dll_list[srcaddr])
        return txt

