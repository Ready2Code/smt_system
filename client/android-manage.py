#!/usr/bin/env python
from __future__ import unicode_literals
import os
import sys
import traceback
import thread
import time
import socket
#aaa = 1

def doit(val):
    global aaa
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "client.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            traceback.print_exc()
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    print "execute_from_command_line"
    #execute_from_command_line(['android-manage.py','makemigrations'])
    #executde_from_cdommand_lidne(['android-manage.py', 'migrate'])
    execute_from_command_line(['android-manage.py', 'runserver', '0.0.0.0:9733'])



if __name__ == "__main__":
    try:
        import starglobal

        starglobal.StarcoreService = StarcoreService
        starglobal.platform = 'Android'
        thread.start_new_thread(doit, (0,))
        while True:
            while libstarpy._SRPDispatch(False) == True:
                pass
            libstarpy._SRPUnLock()
            time.sleep(0.01)
            libstarpy._SRPLock()

    except Exception:
        traceback.print_exc()
