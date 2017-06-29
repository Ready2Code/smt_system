# -*- coding: utf-8 -*-
from ctypes import *
import thread
from threading import Thread

dll_list={}

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

def ts_adapter_thread(mode, srcaddr, destaddr):
    global dll_list 
    dll = init()
    dll_list[srcaddr] = dll
    srcaddr_tuple=get_ip_and_port_from_addr(srcaddr)
    destaddr_tuple=get_ip_and_port_from_addr(destaddr)
    dll.set_and_start.argtypes = [c_char_p, c_char_p, c_int, c_char_p, c_int]
    dll.set_and_start( mode, srcaddr_tuple[0],srcaddr_tuple[1], destaddr_tuple[0],destaddr_tuple[1] )
    return

def start_ts_adapter(mode, srcaddr, destaddr):
    global dll_list 
    if dll_list.has_key(srcaddr):
        return
    t = Thread(target=ts_adapter_thread,args=(mode, srcaddr, destaddr))
    t.setDaemon(True)
    t.start()
    pass 

def stop_ts_adapter(srcaddr):
    global dll_list 
    if dll_list.has_key(srcaddr):
        dll_list[srcaddr].argtypes = [c_char_p]
        dll_list[srcaddr].stop(srcaddr)
        del dll_list[srcaddr]
    
