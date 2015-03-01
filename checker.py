#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement
import os
from fabric.api import local, settings, abort, cd
from fabric.operations import run, put
import fab_utils
import platform
import types



class SystemChecker(object):
    WINDOWS_FLAG = 'Windows'
    LINUX_FLAG = 'Linux'

    @classmethod
    def get_system(cls):
        return platform.system()

    @classmethod
    def is_windows(cls):
        if cls.get_system() == cls.WINDOWS_FLAG:
            return True
        else:
            return False
        pass

    @classmethod
    def is_linux(cls):
        if cls.get_system() == cls.LINUX_FLAG:
            return True
        else:
            return False
        pass



class Checker(object):

    def __init__(self):
        pass

    def check_process(self, process):
        if type(process) in [types.ListType, types.TupleType]:
            cmd = 'pidof %s' % ','.join(process)
        else:
            raise Exception('invalid param format of process name')

        if run(cmd).succeeded:
            return True
        else:
            False
        pass

    def check_port(self, port):
        all_alive = True
        if type(port) in [types.ListType, types.TupleType]:
            for p in port:
                cmd = 'ss -ant  src :{port}|grep {port}'.format(port=p)
                if run(cmd).failed:
                    all_alive = False
                    break
        else:
            raise Exception('invalid param format of port')

        return all_alive
