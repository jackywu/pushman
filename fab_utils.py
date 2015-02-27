#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement
from fabric.operations import run, put

def run_check_failed(cmd,exp):
    result = run(cmd)
    if result.failed:
        raise Exception("%s, %s" % (exp, result))
