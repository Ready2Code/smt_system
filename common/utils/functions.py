# -*- coding: utf-8 -*-
from ctypes import *
import thread
from threading import Thread
import os
import re

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
